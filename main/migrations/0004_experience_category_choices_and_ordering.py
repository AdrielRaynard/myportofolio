from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_populate_education'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experience',
            options={'ordering': ['-started_at']},
        ),
        migrations.AlterField(
            model_name='experience',
            name='category',
            field=models.CharField(choices=[('internship', 'Internship'), ('research', 'Research'), ('volunteer', 'Volunteer'), ('part-time', 'Part-Time'), ('full-time', 'Full-Time'), ('freelance', 'Freelance'), ('kepanitiaan', 'Kepanitiaan'), ('organisasi', 'Organisasi')], default='full-time', max_length=20),
        ),
    ]