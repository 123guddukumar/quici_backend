from django.db import migrations, models
import django.db.models.deletion

def migrate_city_data(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    Restaurant = apps.get_model('users', 'Restaurant')
    City = apps.get_model('users', 'City')
    
    # Migrate CustomUser.city
    for user in CustomUser.objects.all():
        if user.city:  # Assuming city is still a CharField at this point
            city, created = City.objects.get_or_create(name=user.city)
            user.city_temp = city.id  # Store the City ID in a temporary field
            user.save()
    
    # Migrate Restaurant.city
    for restaurant in Restaurant.objects.all():
        if restaurant.city:  # Assuming city is still a CharField at this point
            city, created = City.objects.get_or_create(name=restaurant.city)
            restaurant.city_temp = city.id  # Store the City ID in a temporary field
            restaurant.save()

def reverse_migrate_city_data(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    Restaurant = apps.get_model('users', 'Restaurant')
    City = apps.get_model('users', 'City')
    
    # Reverse CustomUser.city
    for user in CustomUser.objects.all():
        if user.city_temp:
            try:
                city = City.objects.get(id=user.city_temp)
                user.city = city.name  # Restore the city name
                user.save()
            except City.DoesNotExist:
                user.city = None
                user.save()
    
    # Reverse Restaurant.city
    for restaurant in Restaurant.objects.all():
        if restaurant.city_temp:
            try:
                city = City.objects.get(id=restaurant.city_temp)
                restaurant.city = city.name  # Restore the city name
                restaurant.save()
            except City.DoesNotExist:
                restaurant.city = None
                restaurant.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_delete_address'),  # Ensure this matches your actual previous migration
        ('menu', '0003_address_notification_offer'),
    ]

    operations = [
        # Add temporary fields to store City IDs
        migrations.AddField(
            model_name='CustomUser',
            name='city_temp',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='Restaurant',
            name='city_temp',
            field=models.IntegerField(null=True, blank=True),
        ),
        # Run data migration to populate city_temp for both models
        migrations.RunPython(migrate_city_data, reverse_migrate_city_data),
        # Remove old city fields
        migrations.RemoveField(
            model_name='CustomUser',
            name='city',
        ),
        migrations.RemoveField(
            model_name='Restaurant',
            name='city',
        ),
        # Add new city ForeignKey fields
        migrations.AddField(
            model_name='CustomUser',
            name='city',
            field=models.ForeignKey(
                'users.City',
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
            ),
        ),
        migrations.AddField(
            model_name='Restaurant',
            name='city',
            field=models.ForeignKey(
                'users.City',
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
            ),
        ),
        # Copy city_temp to city for both models
        migrations.RunPython(
            code=lambda apps, schema_editor: (
                apps.get_model('users', 'CustomUser').objects.update(city=models.F('city_temp')),
                apps.get_model('users', 'Restaurant').objects.update(city=models.F('city_temp'))
            ),
            reverse_code=lambda apps, schema_editor: None,
        ),
        # Remove temporary city_temp fields
        migrations.RemoveField(
            model_name='CustomUser',
            name='city_temp',
        ),
        migrations.RemoveField(
            model_name='Restaurant',
            name='city_temp',
        ),
        # Rest of the operations from the original migration
        migrations.AlterModelOptions(
            name='CustomUser',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.RemoveField(
            model_name='CustomUser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='CustomUser',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='default_address',
            field=models.ForeignKey(
                'menu.Address',
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='default_for_user',
            ),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='nearest_place',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='receive_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='restaurant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='staff',
                to='users.restaurant',
            ),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='street',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='theme_preference',
            field=models.CharField(
                choices=[('light', 'Light'), ('dark', 'Dark')],
                default='light',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='zip_code',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='CustomUser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='CustomUser',
            name='mobile',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='Restaurant',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='restaurant_profile',
                to='users.customuser',
            ),
        ),
    ]