from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class Student:
    student_id: str
    name: str
    age: int
    grade: str
    email: str


class StudentManagementSystem:
    def __init__(self, data_file: str = "students.json") -> None:
        self.data_file = Path(data_file)
        self.students: Dict[str, Student] = {}
        self._load()

    def _load(self) -> None:
        if not self.data_file.exists():
            return
        try:
            raw = json.loads(self.data_file.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                self.students = {}
                return
            for item in raw:
                student = Student(**item)
                self.students[student.student_id] = student
        except (json.JSONDecodeError, TypeError, ValueError):
            self.students = {}

    def _save(self) -> None:
        payload = [asdict(student) for student in self.students.values()]
        self.data_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_student(self, student: Student) -> bool:
        if student.student_id in self.students:
            return False
        self.students[student.student_id] = student
        self._save()
        return True

    def update_student(self, student_id: str, **updates: object) -> bool:
        student = self.students.get(student_id)
        if not student:
            return False
        valid_fields = set(Student.__dataclass_fields__.keys())
        valid_fields.discard("student_id")
        for field_name, value in updates.items():
            if field_name not in valid_fields:
                return False
        for field_name, value in updates.items():
            if value is not None:
                setattr(student, field_name, value)
        self._save()
        return True

    def delete_student(self, student_id: str) -> bool:
        if student_id not in self.students:
            return False
        del self.students[student_id]
        self._save()
        return True

    def get_student(self, student_id: str) -> Student | None:
        return self.students.get(student_id)

    def list_students(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.student_id)


def _prompt_non_empty(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Value cannot be empty.")


def _prompt_int(message: str) -> int:
    while True:
        raw = input(message).strip()
        if raw.isdecimal() and int(raw) > 0:
            return int(raw)
        print("Please enter a valid positive number.")


def run_cli() -> None:
    sms = StudentManagementSystem()

    menu = """
Student Management System
1. Add student
2. View student
3. List students
4. Update student
5. Delete student
6. Exit
"""

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            student = Student(
                student_id=_prompt_non_empty("Student ID: "),
                name=_prompt_non_empty("Name: "),
                age=_prompt_int("Age: "),
                grade=_prompt_non_empty("Grade: "),
                email=_prompt_non_empty("Email: "),
            )
            if sms.add_student(student):
                print("Student added successfully.")
            else:
                print("Student ID already exists.")

        elif choice == "2":
            student_id = _prompt_non_empty("Student ID: ")
            student = sms.get_student(student_id)
            if student:
                print(asdict(student))
            else:
                print("Student not found.")

        elif choice == "3":
            students = sms.list_students()
            if not students:
                print("No students found.")
            else:
                for student in students:
                    print(asdict(student))

        elif choice == "4":
            student_id = _prompt_non_empty("Student ID to update: ")
            if not sms.get_student(student_id):
                print("Student not found.")
                continue

            print("Leave a field blank to keep the current value.")
            name = input("New name: ").strip() or None
            age_raw = input("New age: ").strip()
            age = None
            invalid_age = False
            if age_raw.isdecimal():
                age_value = int(age_raw)
                if age_value > 0:
                    age = age_value
                else:
                    invalid_age = True
            elif age_raw:
                invalid_age = True
            grade = input("New grade: ").strip() or None
            email = input("New email: ").strip() or None

            if invalid_age:
                print("Invalid age input; age will remain unchanged.")
            if sms.update_student(student_id, name=name, age=age, grade=grade, email=email):
                print("Student updated successfully.")
            else:
                print("Failed to update student.")

        elif choice == "5":
            student_id = _prompt_non_empty("Student ID to delete: ")
            if sms.delete_student(student_id):
                print("Student deleted successfully.")
            else:
                print("Student not found.")

        elif choice == "6":
            print("Goodbye!")
            return

        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    run_cli()
