# Generated by Django 5.0.7 on 2024-07-10 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_remove_companyinformation_city_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('question_index', models.IntegerField()),
                ('response', models.CharField(max_length=100)),
            ],
        ),
    ]