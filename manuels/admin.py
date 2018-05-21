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


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    pass
