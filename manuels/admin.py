from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

from manuels.models import Teacher, Book, Level, Editor, SuppliesRequirement


class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('first_name', 'last_name', 'email', 'phone_number')


@admin.register(Teacher)
class TeacherAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ['full_name', 'email', 'phone_number']

    def send_link(self, request, queryset):
        for teacher in queryset:
            teacher.send_link(request)

    send_link.short_description = 'Envoyer le lien'

    actions = [send_link]


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass


class BookResource(resources.ModelResource):
    class Meta:
        model = Book
        fields = ('title', 'authors', 'editor__name', 'publication_year', 'isbn',
                  'price', 'previously_acquired', 'teacher__first_name', 'teacher__last_name', 'level__name', 'field')
        export_order = ('field', 'title', 'authors', 'editor__name', 'publication_year', 'isbn', 'price',
                        'previously_acquired', 'teacher__first_name', 'teacher__last_name', 'level__name')


@admin.register(Book)
class BookAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BookResource
    list_display = ['level', 'field', 'title', 'authors', 'editor', 'publication_year', 'isbn',
                    'price', 'previously_acquired', 'teacher', 'done']
    list_filter = ['done', 'editor', 'previously_acquired', 'teacher', 'level']
    list_display_links = ['title']
    fieldsets = [
        ('Infos livre', {
            'fields': ('title', 'authors', 'editor', 'publication_year', 'isbn', 'created_at', 'updated_at')
        }),
        ('Élève', {
            'fields': ('price', 'previously_acquired',)
        }),
        ('Coordonnateur', {
            'fields': ('teacher', 'level', 'field')
        }),
        ('Gestion', {
            'fields': ('done',)
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    pass


class SuppliesResource(resources.ModelResource):
    class Meta:
        model = SuppliesRequirement
        fields = ('supplies', 'fields', 'level__name', 'teacher__first_name', 'teacher__last_name')
        export_order = ('fields', 'supplies', 'teacher__first_name', 'teacher__last_name', 'level__name')


@admin.register(SuppliesRequirement)
class SuppliesRequirementAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = SuppliesResource
    list_display = ['id', 'teacher', 'level', 'fields', 'supplies', 'done']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['done', 'teacher', 'level']
