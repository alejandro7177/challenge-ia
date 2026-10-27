import os
import django
from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservas.web.settings")
django.setup()

from reservas.storage import SQLiteStorage
from reservas.service import create_reservation

class DjangoWebTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.storage = SQLiteStorage()
        self.storage.init_db()

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MIC-01")

    def test_unit_list_view(self):
        response = self.client.get(reverse('unit_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Microscopio digital")

    def test_availability_view(self):
        future_start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT10:00")
        future_end = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT11:00")
        response = self.client.get(reverse('availability'), {
            'unit_id': 'MIC-01',
            'start': future_start,
            'end': future_end
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DISPONIBLE")

    def test_reserve_and_cancel_flow(self):
        future_start = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT10:00")
        future_end = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT11:00")
        
        response = self.client.post(reverse('reserve'), {
            'unit_id': 'MIC-01',
            'requester': 'María Pérez',
            'start': future_start,
            'end': future_end
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('reservation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "María Pérez")

        reservas = self.storage.get_reservations(unit_id="MIC-01")
        res_id = reservas[0].id

        response = self.client.post(reverse('cancel_reservation', args=[res_id]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('reservation_list') + '?status=cancelled')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cancelada")
