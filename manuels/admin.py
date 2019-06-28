from django.contrib import admin, messages
from import_export import resources
from import_export.admin import ExportMixin

from manuels.models import Teacher, Book, Level, Editor, SuppliesRequirement, CommonSupply


class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('first_name', 'last_name', 'email', 'phone_number')


@admin.register(Teacher)
class TeacherAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ['full_name', 'email', 'phone_number', 'has_confirmed_list']

    def send_link(self, request, queryset):
        for teacher in queryset:
            teacher.send_link(request)
        messages.success(request, f'Le lien a bien été envoyé aux {queryset.count()} coordonateur(s) sélectionné(s).')

    send_link.short_description = 'Envoyer le lien'

    actions = [send_link]


class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('first_name', 'last_name', 'email', 'phone_number')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'book_count', 'consumable_count', 'consumable_price']
    list_editable = ['order']
    list_display_links = ['name']

    def consumable_count(self, obj: Level):
        return obj.consumable_count
    consumable_count.short_description = 'Nombre de consommable(s)'

    def book_count(self, obj: Level):
        return obj.book_set.count()
    book_count.short_description = 'Nombre de livre(s)'

    def consumable_price(self, obj: Level):
        return f'{obj.consumable_price:.2f}€'
    consumable_price.short_description = 'Coût des consommables'


class BookResource(resources.ModelResource):
    class Meta:
        model = Book
        fields = ('title', 'authors', 'editor__name', 'publication_year', 'isbn', 'comments', 'other_editor',
                  'price', 'previously_acquired', 'teacher__first_name', 'teacher__last_name', 'level__name', 'field',
                  'consumable')
        export_order = ('level__name', 'field', 'title', 'authors', 'editor__name', 'publication_year', 'isbn', 'price',
                        'other_editor', 'previously_acquired', 'teacher__first_name', 'teacher__last_name', 'comments',
                        'consumable')


@admin.register(Book)
class BookAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = BookResource
    list_display = ['level', 'field', 'title', 'authors', 'editor', 'other_editor', 'publication_year', 'isbn',
                    'price', 'previously_acquired', 'teacher', 'done', 'consumable']
    list_editable = ['done']
    list_filter = ['done', 'previously_acquired', 'consumable', 'level', 'editor', 'teacher']
    list_display_links = ['title']
    fieldsets = [
        ('Infos livre', {
            'fields': ('title', 'consumable', 'authors', ('editor', 'other_editor'), 'publication_year',
                       'isbn', 'created_at', 'updated_at', 'comments')
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


@admin.register(CommonSupply)
class CommonSupplyAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_display_links = ['name']
    list_editable = ['order']


class SuppliesResource(resources.ModelResource):
    class Meta:
        model = SuppliesRequirement
        fields = ('supplies', 'field', 'level__name', 'teacher__first_name', 'teacher__last_name')
        export_order = ('level__name', 'field', 'supplies', 'teacher__first_name', 'teacher__last_name')


@admin.register(SuppliesRequirement)
class SuppliesRequirementAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = SuppliesResource
    list_display = ['id', 'teacher', 'level', 'field', 'supplies', 'done']
    list_editable = ['done']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['done', 'teacher', 'level']
