import pytest

try:
    import frappe
    from frappe import exceptions, new_doc, utils
    from frappe.tests.utils import FrappeTestCase
except ImportError:  # pragma: no cover - frappe not installed
    pytest.skip("frappe not available", allow_module_level=True)


class TestServiceProject(FrappeTestCase):
    def _create_project(self, name: str):
        doc = new_doc("Service Project")
        doc.project_name = name
        doc.contract_no = "CN-" + frappe.generate_hash(length=5)
        doc.client = "_Test Customer"
        doc.start_date = utils.now_datetime()
        doc.end_date = utils.add_days(doc.start_date, 1)
        return doc

    def _make_service_object(self, name: str, project: str) -> str:
        obj = new_doc("Service Object")
        obj.object_name = name
        obj.address = "Test address"
        obj.project = project
        obj.insert()
        return obj.name

    def test_date_validation(self):
        doc = self._create_project("Proj1")
        doc.end_date = utils.add_days(doc.start_date, -1)
        with pytest.raises(exceptions.ValidationError):
            doc.validate()

    def test_valid_date_range(self):
        doc = self._create_project("Proj2")
        doc.validate()

    def test_object_cannot_be_linked_to_multiple_projects(self):
        proj1 = self._create_project("ProjA")
        proj1.insert()
        obj_name = self._make_service_object("OBJ-1", proj1.name)
        proj1.append("objects", {"service_object": obj_name})
        proj1.save()

        proj2 = self._create_project("ProjB")
        proj2.append("objects", {"service_object": obj_name})
        with pytest.raises(exceptions.ValidationError):
            proj2.insert()

    def test_duplicate_objects_in_same_project(self):
        proj = self._create_project("ProjC")
        proj.insert()
        obj_name = self._make_service_object("OBJ-2", proj.name)
        proj.append("objects", {"service_object": obj_name})
        proj.append("objects", {"service_object": obj_name})
        with pytest.raises(exceptions.ValidationError):
            proj.save()
