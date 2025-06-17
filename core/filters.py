from django.contrib.admin  import  SimpleListFilter

class HasImageFilter(SimpleListFilter):
    title = 'Imagem'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Com Imagem'),
            ('0', 'Sem Imagem'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(image='')
        elif self.value() == '0':
            return queryset.filter(image='')
        return queryset