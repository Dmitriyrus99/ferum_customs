import pytest
from frappe import exceptions, new_doc, utils
from frappe.tests.utils import FrappeTestCase


class TestServiceProject(FrappeTestCase):
    def test_date_validation(self):
        """Test that end_date cannot be before start_date."""
        doc = new_doc("Service Project")
        doc.start_date = utils.now_datetime()
        doc.end_date = utils.add_days(doc.start_date, -1)

        with pytest.raises(exceptions.ValidationError):
            doc.validate()

    def test_valid_date_range(self):
        """Test that valid date ranges do not raise validation errors."""
        doc = new_doc("Service Project")
        doc.start_date = utils.now_datetime()
        doc.end_date = utils.add_days(doc.start_date, 1)

        # This should not raise any exceptions
        doc.validate()  # Ensure that no exceptions are raised

    def _make_service_object(self, name: str) -> str:
        obj = new_doc("Service Object")
        obj.object_name = name
        obj.insert()
        return obj.name

    def test_object_cannot_be_linked_to_multiple_projects(self):
        obj_name = self._make_service_object("OBJ-1")

        proj1 = new_doc("Service Project")
        proj1.project_name = "Proj1"
        proj1.append("service_objects", {"service_object": obj_name})
        proj1.insert()

        proj2 = new_doc("Service Project")
        proj2.project_name = "Proj2"
        proj2.append("service_objects", {"service_object": obj_name})

        with pytest.raises(exceptions.ValidationError):
            proj2.insert()

    def test_duplicate_objects_in_same_project(self):
        obj_name = self._make_service_object("OBJ-2")
        proj = new_doc("Service Project")
        proj.project_name = "Proj3"
        proj.append("service_objects", {"service_object": obj_name})
        proj.append("service_objects", {"service_object": obj_name})

        with pytest.raises(exceptions.ValidationError):
            proj.insert()
