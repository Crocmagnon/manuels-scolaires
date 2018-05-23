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


@admin.register(Book)
class BookAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BookResource
    list_display = ['title', 'authors', 'editor', 'publication_year', 'isbn',
                    'price', 'previously_acquired', 'teacher', 'level', 'field']
    list_filter = ['editor', 'previously_acquired', 'teacher', 'level']
    fieldsets = [
        ('Infos livre', {
            'fields': ('title', 'authors', 'editor', 'publication_year', 'isbn', 'created_at', 'updated_at')
        }),
        ('Élève', {
            'fields': ('price', 'previously_acquired',)
        }),
        ('Enseignant', {
            'fields': ('teacher', 'level', 'field')
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    pass


class SuppliesResource(resources.ModelResource):
    class Meta:
        model = SuppliesRequirement
        fields = ('supplies', 'level__name', 'teacher__first_name', 'teacher__last_name')


@admin.register(SuppliesRequirement)
class SuppliesRequirementAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = SuppliesResource
    list_display = ['teacher', 'level', 'supplies']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['teacher', 'level']
