from django.core.management.base import BaseCommand
from market.models import Skin

class Command(BaseCommand):
    help = 'Adds test skins to the database'

    def handle(self, *args, **kwargs):
        # Create test skin data
        skins_data = [
            {'name': 'AK-47 | Asiimov', 'price': 50.00, 'image': 'skins/1.jpg'},
            {'name': 'M4A4 | Howl', 'price': 1500.00, 'image': 'skins/2.jpg'},
            {'name': 'AWP | Dragon Lore', 'price': 2000.00, 'image': 'skins/3.jpg'},
            {'name': 'Butterfly Knife | Fade', 'price': 800.00, 'image': 'skins/4.jpg'},
            {'name': 'Desert Eagle | Blaze', 'price': 200.00, 'image': 'skins/5.png'},
            {'name': 'M4A1-S | Hyper Beast', 'price': 45.00, 'image': 'skins/6.jpg'},
            {'name': 'AWP | Medusa', 'price': 1200.00, 'image': 'skins/7.jpg'},
            {'name': 'Karambit | Doppler', 'price': 600.00, 'image': 'skins/8.jpg'},
            {'name': 'USP-S | Kill Confirmed', 'price': 35.00, 'image': 'skins/9.jpg'},
            {'name': 'Glock-18 | Fade', 'price': 300.00, 'image': 'skins/10.jpg'},
            {'name': 'M4A4 | Neo-Noir', 'price': 40.00, 'image': 'skins/11.jpg'},
            {'name': 'AK-47 | Fire Serpent', 'price': 800.00, 'image': 'skins/12.jpg'},
            {'name': 'AWP | Lightning Strike', 'price': 150.00, 'image': 'skins/13.jpg'},
            {'name': 'Bayonet | Marble Fade', 'price': 500.00, 'image': 'skins/14.jpg'},
            {'name': 'Desert Eagle | Golden Koi', 'price': 25.00, 'image': 'skins/15.jpg'},
            {'name': 'P90 | Death by Kitty', 'price': 100.00, 'image': 'skins/16.jpg'},
            {'name': 'M4A1-S | Hot Rod', 'price': 120.00, 'image': 'skins/17.jpg'},
            {'name': 'AWP | Asiimov', 'price': 80.00, 'image': 'skins/18.jpg'},
            {'name': 'Flip Knife | Tiger Tooth', 'price': 300.00, 'image': 'skins/19.jpg'},
            {'name': 'P250 | Muertos', 'price': 15.00, 'image': 'skins/20.jpg'},
            {'name': 'AK-47 | Vulcan', 'price': 70.00, 'image': 'skins/21.jpg'},
            {'name': 'M4A4 | Poseidon', 'price': 250.00, 'image': 'skins/22.jpg'},
            {'name': 'AWP | Containment Breach', 'price': 90.00, 'image': 'skins/23.jpg'},
            {'name': 'Huntsman Knife | Crimson Web', 'price': 400.00, 'image': 'skins/24.jpg'},
            {'name': 'USP-S | Neo-Noir', 'price': 30.00, 'image': 'skins/25.jpg'},
            {'name': 'AK-47 | Bloodsport', 'price': 60.00, 'image': 'skins/26.jpg'},
            {'name': 'M4A1-S | Mecha Industries', 'price': 35.00, 'image': 'skins/27.jpg'},
            {'name': 'AWP | Neo-Noir', 'price': 75.00, 'image': 'skins/28.jpg'}
        ]

        for skin_data in skins_data:
            skin, created = Skin.objects.update_or_create(
                name=skin_data['name'],
                defaults={
                    'price': skin_data['price'],
                    'image': skin_data['image']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created skin "{skin_data["name"]}"')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated skin "{skin_data["name"]}"')
                ) 