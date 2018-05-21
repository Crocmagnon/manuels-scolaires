from django.contrib import admin

from manuels.models import Teacher, Book, Level, Editor


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone_number']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'editor', 'collection', 'publication_year', 'isbn',
                    'price', 'previously_acquired', 'teacher', 'level', 'field']
    list_filter = ['editor', 'previously_acquired', 'teacher', 'level']
    fieldsets = [
        ('Infos livre', {
            'fields': ('title', 'authors', 'editor', 'collection', 'publication_year', 'isbn', 'created_at', 'updated_at')
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
