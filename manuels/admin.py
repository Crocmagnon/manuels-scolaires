from django.contrib import admin, messages
from import_export import resources, fields
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


class LevelResource(resources.ModelResource):
    non_acquired_book_count = fields.Field(attribute='non_acquired_book_count')
    non_acquired_book_price = fields.Field(attribute='non_acquired_book_price')
    non_acquired_consumable_count = fields.Field(attribute='non_acquired_consumable_count')
    non_acquired_consumable_price = fields.Field(attribute='non_acquired_consumable_price')
    non_acquired_total_price = fields.Field(attribute='non_acquired_total_price')

    class Meta:
        model = Level
        fields = (
            'name',
            'non_acquired_book_count',
            'non_acquired_book_price',
            'non_acquired_consumable_count',
            'non_acquired_consumable_price',
            'non_acquired_total_price',
        )
        export_order = (
            'name',
            'non_acquired_book_count',
            'non_acquired_book_price',
            'non_acquired_consumable_count',
            'non_acquired_consumable_price',
            'non_acquired_total_price',
        )


@admin.register(Level)
class LevelAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = LevelResource
    list_display = [
        'name',
        'order',
        'non_acquired_book_count',
        'non_acquired_book_price',
        'non_acquired_consumable_count',
        'non_acquired_consumable_price',
        'non_acquired_total_price',
    ]
    list_editable = ['order']
    list_display_links = ['name']

    def non_acquired_book_count(self, obj: Level):
        return obj.non_acquired_book_count
    non_acquired_book_count.short_description = 'Nombre de livres à acheter (hors consommables)'

    def non_acquired_book_price(self, obj: Level):
        return f'{obj.non_acquired_book_price:.2f}€'
    non_acquired_book_price.short_description = 'Coût des livres à acheter (hors consommables)'

    def non_acquired_consumable_count(self, obj: Level):
        return obj.non_acquired_consumable_count
    non_acquired_consumable_count.short_description = 'Nombre de consommables à acheter'

    def non_acquired_consumable_price(self, obj: Level):
        return f'{obj.non_acquired_consumable_price:.2f}€'
    non_acquired_consumable_price.short_description = 'Coût des consommables à acheter'

    def non_acquired_total_price(self, obj: Level):
        return f'{obj.non_acquired_total_price:.2f}€'
    non_acquired_total_price.short_description = 'Coût total à acheter'


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
