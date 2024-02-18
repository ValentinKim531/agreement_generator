from django.db import models


class DocumentTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_file = models.FileField(
        upload_to='agreements_templates/'
    )

    def __str__(self):
        return (f"Название {self.name} для шаблона "
                f"договора {self.template_file}")

    class Meta:
        verbose_name = 'Шаблон договора'
        verbose_name_plural = 'Шаблоны договоров'
