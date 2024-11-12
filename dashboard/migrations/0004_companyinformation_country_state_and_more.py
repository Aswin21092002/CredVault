# Generated by Django 4.2.7 on 2023-11-26 18:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_alter_companyinformation_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="companyinformation",
            name="country_state",
            field=models.CharField(default="california", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="companyinformation",
            name="business_address",
            field=models.CharField(max_length=255),
        ),
    ]