from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Car, Manufacturer


class TestHomePage(TestCase):
    def setUp(self):
        self.driver = get_user_model().objects.create_user(
            username="TestUser1", password="TestPassword1"
        )

    def test_home_page_login_required(self):
        response = self.client.get(reverse("taxi:index"))
        self.assertNotEqual(response.status_code, 200)

    def test_home_page(self):
        self.client.force_login(self.driver)
        response = self.client.get(reverse("taxi:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/index.html")


class TestCarViewsLoginRequired(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="TestManufacturer",
            country="TestCountry",
        )
        self.car = Car.objects.create(
            model="TestModel",
            manufacturer=self.manufacturer,
        )

    def test_car_list_login_required(self):
        response = self.client.get(reverse("taxi:car-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_car_detail_login_required(self):
        response = self.client.get(
            reverse("taxi:car-detail", args=[self.car.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_car_create_login_required(self):
        response = self.client.get(reverse("taxi:car-create"))
        self.assertNotEqual(response.status_code, 200)

    def test_car_update_login_required(self):
        response = self.client.get(
            reverse("taxi:car-update", args=[self.car.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_car_delete_login_required(self):
        response = self.client.get(
            reverse("taxi:car-delete", args=[self.car.id])
        )
        self.assertNotEqual(response.status_code, 200)


class BaseCarTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="TestManufacturer",
            country="TestCountry",
        )
        self.car = Car.objects.create(
            model="TestModel",
            manufacturer=self.manufacturer,
        )
        self.driver = get_user_model().objects.create_user(
            username="TestUser1", password="TestPassword1"
        )
        self.car.drivers.add(self.driver)
        self.client.force_login(self.driver)


class TestCarList(BaseCarTest):
    car_list_url = reverse("taxi:car-list")
    paginated_by = 5

    def setUp(self):
        super().setUp()
        for i in range(1, 16):
            car = Car.objects.create(
                model=f"TestModel{i}",
                manufacturer=self.manufacturer,
            )
            car.drivers.add(self.driver)

    def test_car_list_template(self):
        response = self.client.get(self.car_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_car_list_pagination(self):
        response = self.client.get(self.car_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(
            len(response.context["car_list"]), self.paginated_by
        )

    def test_car_list_search(self):
        response = self.client.get(self.car_list_url + "?model=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["car_list"]), 2)
        self.assertContains(response, "TestModel4")
        self.assertNotContains(response, "TestModel5")


class TestCarDetail(BaseCarTest):
    def test_car_detail_tamplate(self):
        response = self.client.get(
            reverse("taxi:car-detail", args=[self.car.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_detail.html")


class TestCarCreate(BaseCarTest):
    def test_car_create_template(self):
        response = self.client.get(reverse("taxi:car-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_form.html")

    def test_car_create(self):
        data = {
            "model": "NewTestModel",
            "manufacturer": self.manufacturer.id,
            "drivers": [self.driver.id],
        }
        self.client.post(reverse("taxi:car-create"), data=data)
        new_car = Car.objects.get(model=data["model"])
        self.assertEqual(new_car.model, data["model"])
        self.assertEqual(new_car.manufacturer, self.manufacturer)
        self.assertIn(self.driver, new_car.drivers.all())


class TestCarUpdate(BaseCarTest):
    def test_car_update_template(self):
        response = self.client.get(
            reverse("taxi:car-update", args=[self.car.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_form.html")

    def test_car_update(self):
        car = Car.objects.create(
            model="OldTestModel",
            manufacturer=self.manufacturer,
        )
        new_manufacturer = Manufacturer.objects.create(
            name="NewTestManufacturer",
            country="TestCountry",
        )
        new_driver = get_user_model().objects.create_user(
            username="TestDriver2",
            password="TestPassword2",
            license_number="TST12345",
        )
        form_data = {
            "model": "NewTestModel",
            "manufacturer": new_manufacturer.id,
            "drivers": [self.driver.id, new_driver.id],
        }
        self.client.post(
            reverse("taxi:car-update", args=[car.id]),
            data=form_data
        )
        updated_car = Car.objects.get(id=car.id)
        self.assertEqual(updated_car.model, form_data["model"])
        self.assertEqual(updated_car.manufacturer, new_manufacturer)
        self.assertIn(new_driver, updated_car.drivers.all())


class TestCarDelete(BaseCarTest):
    def test_car_delete_template(self):
        response = self.client.get(
            reverse("taxi:car-delete", args=[self.car.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_confirm_delete.html")

    def test_car_delete(self):
        self.client.post(reverse("taxi:car-delete", args=[self.car.id]))
        cars = Car.objects.filter(id=self.car.id)
        self.assertEqual(len(cars), 0)

    # I'm tired, boss


class TestManufacturerViewsLoginRequired(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="TestManufacturer",
            country="TestCountry",
        )

    def test_manufacturer_list_login_required(self):
        response = self.client.get(reverse("taxi:manufacturer-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_manufacturer_create_login_required(self):
        response = self.client.get(reverse("taxi:manufacturer-create"))
        self.assertNotEqual(response.status_code, 200)

    def test_manufacturer_update_login_required(self):
        response = self.client.get(
            reverse("taxi:manufacturer-update", args=[self.manufacturer.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_manufacturer_delete_login_required(self):
        response = self.client.get(
            reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        )
        self.assertNotEqual(response.status_code, 200)


class BaseManufacturerTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="TestManufacturer",
            country="TestCountry",
        )
        self.driver = get_user_model().objects.create_user(
            username="TestDriver3", password="TestPassword3"
        )
        self.client.force_login(self.driver)


class TestManufacturerList(BaseManufacturerTest):
    manufacturer_list_url = reverse("taxi:manufacturer-list")
    paginated_by = 5

    def setUp(self):
        super().setUp()
        for i in range(1, 16):
            Manufacturer.objects.create(
                name=f"TestManufacturer{i}",
                country=f"TestCountry{i}",
            )

    def test_manufacturer_list_template(self):
        response = self.client.get(self.manufacturer_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    def test_manufacturer_list_pagination(self):
        response = self.client.get(self.manufacturer_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(
            len(response.context["manufacturer_list"]), self.paginated_by
        )

    def test_manufacturer_list_search(self):
        response = self.client.get(self.manufacturer_list_url + "?name=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["manufacturer_list"]), 2)
        self.assertContains(response, "TestManufacturer4")
        self.assertNotContains(response, "TestManufacturer5")


class TestManufacturerCreate(BaseManufacturerTest):
    def test_manufacturer_create_template(self):
        response = self.client.get(reverse("taxi:manufacturer-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/manufacturer_form.html")

    def test_manufacturer_create(self):
        form_data = {
            "name": "NewTestManufacturer",
            "country": "TestCountry",
        }
        self.client.post(reverse("taxi:manufacturer-create"), data=form_data)
        new_manufacturer = Manufacturer.objects.get(name=form_data["name"])
        self.assertEqual(new_manufacturer.name, form_data["name"])
        self.assertEqual(new_manufacturer.country, form_data["country"])


class TestManufacturerUpdate(BaseManufacturerTest):
    def test_manufacturer_update_template(self):
        response = self.client.get(
            reverse("taxi:manufacturer-update", args=[self.manufacturer.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/manufacturer_form.html")

    def test_manufacturer_update(self):
        data = {
            "name": "UpdatedTestManufacturer",
            "country": "UpdatedCountry",
        }
        self.client.post(
            reverse("taxi:manufacturer-update", args=[self.manufacturer.id]),
            data=data,
        )
        updated_manufacturer = Manufacturer.objects.get(
            id=self.manufacturer.id
        )
        self.assertEqual(updated_manufacturer.name, data["name"])
        self.assertEqual(updated_manufacturer.country, data["country"])


class TestManufacturerDelete(BaseManufacturerTest):
    def test_manufacturer_delete_template(self):
        response = self.client.get(
            reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "taxi/manufacturer_confirm_delete.html"
        )

    def test_manufacturer_delete(self):
        self.client.post(
            reverse("taxi:manufacturer-delete", args=[self.manufacturer.id])
        )
        manufacturers = Manufacturer.objects.filter(id=self.manufacturer.id)
        self.assertEqual(len(manufacturers), 0)


class TestDriverViewsLoginRequired(TestCase):
    def setUp(self):
        self.driver = get_user_model().objects.create_user(
            username="TestDriver4", password="TestPassword4"
        )

    def test_driver_list_login_required(self):
        response = self.client.get(reverse("taxi:driver-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_driver_detail_login_required(self):
        response = self.client.get(
            reverse("taxi:driver-detail", args=[self.driver.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_driver_create_login_required(self):
        response = self.client.get(reverse("taxi:driver-create"))
        self.assertNotEqual(response.status_code, 200)

    def test_driver_update_login_required(self):
        response = self.client.get(
            reverse("taxi:driver-update", args=[self.driver.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_driver_delete_login_required(self):
        response = self.client.get(
            reverse("taxi:driver-delete", args=[self.driver.id])
        )
        self.assertNotEqual(response.status_code, 200)


class BaseDriverTest(TestCase):
    def setUp(self):
        self.driver = get_user_model().objects.create_user(
            username="TestDriver5", password="TestPassword5"
        )
        self.client.force_login(self.driver)


class TestDriverList(BaseDriverTest):
    driver_list_url = reverse("taxi:driver-list")
    paginated_by = 5

    def setUp(self):
        super().setUp()
        for i in range(1, 10):
            get_user_model().objects.create_user(
                username=f"UniqueTestDriver{i}",
                password=f"UniqueTestPassword{i}",
                license_number=f"ABC0000{i}",
            )

    def test_driver_list_template(self):
        response = self.client.get(self.driver_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_list.html")

    def test_driver_list_pagination(self):
        response = self.client.get(self.driver_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(
            len(response.context["driver_list"]), self.paginated_by
        )

    def test_driver_list_search(self):
        response = self.client.get(self.driver_list_url + "?username=7")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["driver_list"]), 1)
        self.assertContains(response, "TestDriver7")
        self.assertNotContains(response, "TestDriver8")


class TestDriverDetail(BaseDriverTest):
    def test_driver_detail_template(self):
        response = self.client.get(
            reverse("taxi:driver-detail", args=[self.driver.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_detail.html")


class TestDriverCreate(BaseDriverTest):
    def test_driver_create_template(self):
        response = self.client.get(reverse("taxi:driver-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_form.html")

    def test_driver_create(self):
        data = {
            "username": "NewTestDriver1",
            "password1": "NewTestPassword1",
            "password2": "NewTestPassword1",
            "first_name": "NewTestFirstName1",
            "last_name": "NewTestLastName1",
            "license_number": "OOO00000",
        }
        self.client.post(
            reverse("taxi:driver-create"),
            data=data,
        )
        new_driver = get_user_model().objects.get(username=data["username"])
        self.assertEqual(new_driver.username, data["username"])
        self.assertTrue(new_driver.check_password(data["password1"]))


class TestDriverLicenseUpdate(BaseDriverTest):
    def test_driver_license_update_template(self):
        response = self.client.get(
            reverse("taxi:driver-update", args=[self.driver.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_form.html")

    def test_driver_license_update(self):
        data = {
            "license_number": "UPD00000",
        }
        self.client.post(
            reverse("taxi:driver-update", args=[self.driver.id]),
            data=data,
        )
        updated_driver = get_user_model().objects.get(id=self.driver.id)
        self.assertEqual(
            updated_driver.license_number, data["license_number"]
        )


class TestDriverDelete(BaseDriverTest):
    def test_driver_delete_template(self):
        response = self.client.get(
            reverse("taxi:driver-delete", args=[self.driver.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_confirm_delete.html")

    def test_driver_delete(self):
        self.client.post(reverse("taxi:driver-delete", args=[self.driver.id]))
        drivers = get_user_model().objects.filter(id=self.driver.id)
        self.assertEqual(drivers.count(), 0)
