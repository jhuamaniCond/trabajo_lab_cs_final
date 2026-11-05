# Configura Redmine para el proceso de requerimientos del Sistema Cóndor.
#
#   docker cp configurar_redmine.rb redmine-condor:/tmp/
#   docker exec -e RAILS_ENV=production redmine-condor bundle exec rails runner /tmp/configurar_redmine.rb
#
# Requiere haber cargado antes los datos por defecto en español:
#   docker exec -e REDMINE_LANG=es -e RAILS_ENV=production redmine-condor bundle exec rake redmine:load_default_data

CLAVE = 'Condor2026!'

# --- Ajustes generales -------------------------------------------------------
Setting.default_language = 'es'
Setting.force_default_language_for_anonymous = '1'
Setting.force_default_language_for_loggedin = '1'
Setting.login_required = '1'
Setting.rest_api_enabled = '1'
Setting.app_title = 'Cóndor · Gestión de requisitos'
Setting.date_format = '%d/%m/%Y'
Setting.time_format = '%H:%M'
Setting.text_formatting = 'common_mark'
Setting.default_projects_tracker_ids = []

admin = User.find_by_login('admin')
admin.password = admin.password_confirmation = CLAVE
admin.must_change_passwd = false
admin.language = 'es'
admin.save!
admin.pref.update!(time_zone: 'Lima')

# --- Estados: registrado, analizado, aprobado o rechazado, implementado, verificado y cerrado
Issue.destroy_all
ESTADOS = [
  ['Registrado', false], ['Analizado', false], ['Aprobado', false], ['Rechazado', true],
  ['Implementado', false], ['Verificado', false], ['Cerrado', true]
]
WorkflowRule.delete_all
Tracker.delete_all
IssueStatus.delete_all
estado = {}
ESTADOS.each_with_index do |(nombre, cerrado), i|
  estado[nombre] = IssueStatus.create!(name: nombre, is_closed: cerrado, position: i + 1)
end

# --- Prioridades: las de la ERS (Alta, Media, Baja) ---------------------------
IssuePriority.where(name: %w[Urgente Inmediata]).destroy_all
IssuePriority.find_by(name: 'Normal')&.update!(name: 'Media', is_default: true)

# --- Tipos de petición ---------------------------------------------------------
campos_std = %w[assigned_to_id fixed_version_id priority_id description done_ratio]
requisito = Tracker.create!(name: 'Requisito', default_status: estado['Registrado'], position: 1,
                            description: 'Requisito funcional o no funcional de la ERS',
                            core_fields: campos_std)
cambio = Tracker.create!(name: 'Solicitud de cambio', default_status: estado['Registrado'], position: 2,
                         description: 'Solicitud de cambio a la línea base de requisitos',
                         core_fields: campos_std)

# --- Roles ---------------------------------------------------------------------
Role.where(builtin: 0).destroy_all
permisos = %i[view_issues add_issues edit_issues add_issue_notes view_private_notes
              manage_issue_relations view_issue_watchers add_issue_watchers
              save_queries view_gantt view_calendar view_documents view_files
              view_wiki_pages view_changesets]
roles = {}
[
  ['Analista', permisos],
  ['Comité de cambios (CCB)', permisos],
  ['Desarrollador', permisos],
  ['Evaluador de calidad', permisos],
  ['Responsable de configuración', permisos + %i[manage_versions manage_categories]]
].each_with_index do |(nombre, p), i|
  roles[nombre] = Role.create!(name: nombre, permissions: p, assignable: true, position: i + 1,
                               issues_visibility: 'all')
end

# --- Flujo de trabajo (mismo flujo para requisitos y cambios) ------------------
TRANSICIONES = {
  'Analista' => [%w[Registrado Analizado]],
  'Comité de cambios (CCB)' => [%w[Analizado Aprobado], %w[Analizado Rechazado], %w[Verificado Cerrado]],
  'Desarrollador' => [%w[Aprobado Implementado]],
  'Evaluador de calidad' => [%w[Implementado Verificado], %w[Verificado Implementado]]
}
[requisito, cambio].each do |tracker|
  TRANSICIONES.each do |rol, pares|
    pares.each do |de, a|
      WorkflowTransition.create!(tracker: tracker, role: roles[rol],
                                 old_status: estado[de], new_status: estado[a])
    end
  end
end

# --- Campos personalizados -----------------------------------------------------
IssueCustomField.delete_all
def campo(nombre, formato, trackers, extra = {})
  IssueCustomField.create!({ name: nombre, field_format: formato, is_for_all: true,
                             visible: true, trackers: trackers, searchable: true,
                             is_filter: true }.merge(extra))
end
campo('ID ERS', 'string', [requisito], is_required: true)
campo('Tipo de requisito', 'list', [requisito], possible_values: ['Funcional', 'No funcional'], is_required: true)
campo('Fuente', 'string', [requisito])
campo('Criterio de aceptación', 'text', [requisito], text_formatting: 'full')
campo('Pruebas vinculadas', 'text', [requisito], text_formatting: 'full')
campo('ID cambio', 'string', [cambio], is_required: true)
campo('Motivo', 'text', [cambio], text_formatting: 'full')
campo('Impacto en diseño', 'text', [cambio], text_formatting: 'full')
campo('Impacto en costo', 'string', [cambio])
campo('Impacto en plazo', 'string', [cambio])
campo('Riesgos', 'text', [cambio], text_formatting: 'full')
campo('Pruebas afectadas', 'text', [cambio], text_formatting: 'full')
campo('Decisión', 'list', [cambio], possible_values: %w[Pendiente Aprobada Rechazada], default_value: 'Pendiente')

# --- Usuarios (integrantes y gerente representado) ----------------------------
User.where.not(login: 'admin').where(type: 'User').destroy_all
USUARIOS = [
  ['jhuamani',    'Jeanpiero Sixto',  'Huamani Condori',     ['Analista', 'Comité de cambios (CCB)', 'Desarrollador', 'Evaluador de calidad', 'Responsable de configuración']],
  ['jpayehuanca', 'Jhastyn Jefferson', 'Payehuanca Riquelme', ['Analista', 'Comité de cambios (CCB)', 'Desarrollador', 'Evaluador de calidad', 'Responsable de configuración']],
  ['rcondo',      'Richard Alberto',  'Condo Zamata',        ['Analista', 'Desarrollador', 'Evaluador de calidad', 'Responsable de configuración']],
  ['achaisa',     'Anthony Leonel',   'Chaisa Fernández',    ['Analista', 'Desarrollador', 'Evaluador de calidad', 'Responsable de configuración']],
  ['gerente',     'Gerente general',  '(representado)',      ['Comité de cambios (CCB)']]
]
usuarios = {}
USUARIOS.each do |login, nombre, apellido, _|
  u = User.new(firstname: nombre, lastname: apellido, mail: "#{login}@condor.local", language: 'es')
  u.login = login
  u.password = u.password_confirmation = CLAVE
  u.status = User::STATUS_ACTIVE
  u.save!
  u.pref.update!(time_zone: 'Lima')
  usuarios[login] = u
end

# --- Proyecto, versiones y miembros --------------------------------------------
Project.delete_all
proyecto = Project.create!(name: 'Sistema Cóndor', identifier: 'condor', is_public: false,
                           description: 'Gestión de requisitos y cambios del Sistema de Ventas y Facturación ' \
                                        'Cóndor (Ferretería Cóndor Majes S.A.C.). Línea base: ERS 1.1.',
                           tracker_ids: [requisito.id, cambio.id],
                           enabled_module_names: %w[issue_tracking time_tracking documents files gantt calendar])
proyecto.versions.create!(name: '1.0.0', description: 'Línea base inicial (ERS 1.0, perfil MAESTRO)',
                          effective_date: Date.new(2026, 10, 29), status: 'closed')
proyecto.versions.create!(name: '1.1.0', description: 'ERS 1.1: CC-01 ingreso con usuario, contraseña y roles; API REST',
                          effective_date: Date.new(2026, 10, 30))
USUARIOS.each do |login, _, _, nombres_roles|
  Member.create!(project: proyecto, principal: usuarios[login], roles: nombres_roles.map { |r| roles[r] })
end

puts "Estados: #{IssueStatus.pluck(:name).join(', ')}"
puts "Tipos:   #{Tracker.pluck(:name).join(', ')}"
puts "Roles:   #{Role.givable.pluck(:name).join(', ')}"
puts "Transiciones: #{WorkflowTransition.count}"
puts "Usuarios: #{User.where(type: 'User').pluck(:login).join(', ')}"
puts "Proyecto: #{proyecto.name} (#{proyecto.versions.pluck(:name).join(', ')})"
