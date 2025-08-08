from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from .bot_service import ServiceRequestStates, dispatcher
import frappe

@dispatcher.message_handler(Command("new_request"), state="*")
async def new_request_handler(message: types.Message, state: FSMContext):
    await state.set_state(ServiceRequestStates.waiting_subject)
    await message.answer("Please enter the subject of the service request.")

@dispatcher.message_handler(state=ServiceRequestStates.waiting_subject)
async def subject_handler(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(ServiceRequestStates.waiting_type)
    await message.answer("Please enter the type (Bug, Feature, Question)." )

@dispatcher.message_handler(state=ServiceRequestStates.waiting_type)
async def type_handler(message: types.Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(ServiceRequestStates.waiting_priority)
    await message.answer("Please enter the priority (Low, Medium, High, Urgent)." )

@dispatcher.message_handler(state=ServiceRequestStates.waiting_priority)
async def priority_handler(message: types.Message, state: FSMContext):
    await state.update_data(priority=message.text)
    await state.set_state(ServiceRequestStates.waiting_service_object)
    await message.answer("Please enter the service object.")

@dispatcher.message_handler(state=ServiceRequestStates.waiting_service_object)
async def service_object_handler(message: types.Message, state: FSMContext):
    await state.update_data(service_object=message.text)
    data = await state.get_data()

    # Create Service Request in Frappe
    try:
        doc = frappe.get_doc({
            "doctype": "ServiceRequest",
            "subject": data["subject"],
            "type": data["type"],
            "priority": data["priority"],
            "service_object": data["service_object"],
            "status": "Open"
        })
        doc.insert()
        frappe.db.commit()
        await message.answer(f"Service Request {doc.name} created successfully.")
    except Exception as e:
        await message.answer(f"Failed to create service request: {e}")

    await state.finish()


@dispatcher.message_handler(Command("upload_photo"), state="*")
async def upload_photo_handler(message: types.Message, state: FSMContext):
    await state.set_state(PhotoUploadStates.waiting_request_name)
    await message.answer("Please enter the Service Request name (e.g., SR-00001).")

@dispatcher.message_handler(state=PhotoUploadStates.waiting_request_name)
async def request_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(request_name=message.text)
    await state.set_state(PhotoUploadStates.waiting_photo)
    await message.answer("Please upload the photo.")

@dispatcher.message_handler(content_types=["photo"], state=PhotoUploadStates.waiting_photo)
async def photo_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    request_name = data["request_name"]
    photo = message.photo[-1]

    # Download photo and create CustomAttachment
    try:
        file_info = await dispatcher.bot.get_file(photo.file_id)
        file_content = await dispatcher.bot.download_file(file_info.file_path)

        # Create CustomAttachment
        attachment = frappe.get_doc({
            "doctype": "CustomAttachment",
            "file": file_content.getvalue(),
            "attached_to_doctype": "ServiceRequest",
            "attached_to_name": request_name
        })
        attachment.insert()

        # Link to ServiceRequest
        doc = frappe.get_doc("ServiceRequest", request_name)
        doc.append("photo_attachments", {
            "attachment": attachment.name
        })
        doc.save()
        frappe.db.commit()

        await message.answer("Photo uploaded successfully.")
    except Exception as e:
        await message.answer(f"Failed to upload photo: {e}")

    await state.finish()

@dispatcher.message_handler(Command("my_requests"), state="*")
async def my_requests_handler(message: types.Message, state: FSMContext):
    # Logic to get requests assigned to the user
    await message.answer("This feature is not yet implemented.")

@dispatcher.message_handler(Command("set_status"), state="*")
async def set_status_handler(message: types.Message, state: FSMContext):
    # Logic to change the status of a request
    await message.answer("This feature is not yet implemented.")

@dispatcher.message_handler(Command("get_report"), state="*")
async def get_report_handler(message: types.Message, state: FSMContext):
    # Logic to get and send a report
    await message.answer("This feature is not yet implemented.")