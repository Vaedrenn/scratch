import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QLineEdit,
                               QTextEdit, QPushButton, QListWidget, QListWidgetItem,
                               QMessageBox, QFileDialog, QSplitter, QGroupBox,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SkillDefinitionsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skill Definitions Editor")
        self.setGeometry(100, 100, 800, 700)

        # Store the current data
        self.skill_data = {}
        self.current_skill_id = None

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Create menu bar buttons
        self.create_menu_bar(main_layout)

        # Create main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Skills list
        self.create_skills_list_panel(splitter)

        # Right panel - Skill editor
        self.create_editor_panel(splitter)

        # Set splitter proportions
        splitter.setSizes([300, 500])

        # Load default data
        self.load_default_data()

    def create_menu_bar(self, parent_layout):
        """Create the top menu bar with buttons"""
        menu_layout = QHBoxLayout()

        self.new_button = QPushButton("New Skill")
        self.load_button = QPushButton("Load JSON")
        self.save_button = QPushButton("Save JSON")
        self.preview_button = QPushButton("Preview JSON")
        self.delete_button = QPushButton("Delete Skill")

        # Connect signals
        self.new_button.clicked.connect(self.create_new_skill)
        self.load_button.clicked.connect(self.load_json)
        self.save_button.clicked.connect(self.save_json)
        self.preview_button.clicked.connect(self.preview_json)
        self.delete_button.clicked.connect(self.delete_current_skill)

        # Style buttons
        for btn in [self.new_button, self.load_button, self.save_button,
                    self.preview_button, self.delete_button]:
            btn.setMinimumHeight(30)

        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; }")

        menu_layout.addWidget(self.new_button)
        menu_layout.addWidget(self.load_button)
        menu_layout.addWidget(self.save_button)
        menu_layout.addWidget(self.preview_button)
        menu_layout.addStretch()
        menu_layout.addWidget(self.delete_button)

        parent_layout.addLayout(menu_layout)

    def create_skills_list_panel(self, parent_splitter):
        """Create the left panel with skills list"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Title
        title_label = QLabel("Skills List")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        left_layout.addWidget(title_label)

        # Skills list
        self.skills_list = QListWidget()
        self.skills_list.itemClicked.connect(self.on_skill_selected)
        left_layout.addWidget(self.skills_list)

        # Add count label
        self.count_label = QLabel("0 skills")
        self.count_label.setStyleSheet("color: gray; font-style: italic;")
        left_layout.addWidget(self.count_label)

        parent_splitter.addWidget(left_panel)

    def create_editor_panel(self, parent_splitter):
        """Create the right panel with skill editor"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Create scroll area for the editor
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Editor layout
        editor_layout = QVBoxLayout(scroll_widget)

        # Title
        self.editor_title = QLabel("Skill Editor")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.editor_title.setFont(title_font)
        editor_layout.addWidget(self.editor_title)

        # Create form group
        form_group = QGroupBox("Skill Properties")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)

        # Skill ID field
        form_layout.addWidget(QLabel("Skill ID:"), 0, 0)
        self.skill_id_input = QLineEdit()
        self.skill_id_input.setPlaceholderText("e.g., heal, damage, buff")
        self.skill_id_input.textChanged.connect(self.on_skill_id_changed)
        form_layout.addWidget(self.skill_id_input, 0, 1)

        # Display name field
        form_layout.addWidget(QLabel("Display Name:"), 1, 0)
        self.display_input = QLineEdit()
        self.display_input.setPlaceholderText("e.g., Heal, Fire Blast")
        self.display_input.textChanged.connect(self.on_field_changed)
        form_layout.addWidget(self.display_input, 1, 1)

        # Description field
        form_layout.addWidget(QLabel("Description:"), 2, 0, Qt.AlignTop)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., Heal {value} when played\nUse {value} for dynamic values")
        self.description_input.setMaximumHeight(100)
        self.description_input.textChanged.connect(self.on_field_changed)
        form_layout.addWidget(self.description_input, 2, 1)

        # Help text
        help_label = QLabel("💡 Tip: Use {value} in descriptions for dynamic values that will be replaced at runtime.")
        help_label.setStyleSheet(
            "color: #666; font-style: italic; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        help_label.setWordWrap(True)
        form_layout.addWidget(help_label, 3, 0, 1, 2)

        editor_layout.addWidget(form_group)

        # Action buttons for current skill
        action_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply Changes")
        self.revert_button = QPushButton("Revert Changes")

        self.apply_button.clicked.connect(self.apply_changes)
        self.revert_button.clicked.connect(self.revert_changes)

        self.apply_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.revert_button.setStyleSheet("QPushButton { background-color: #ff9800; color: white; }")

        action_layout.addWidget(self.apply_button)
        action_layout.addWidget(self.revert_button)
        action_layout.addStretch()

        editor_layout.addLayout(action_layout)
        editor_layout.addStretch()

        right_layout.addWidget(scroll_area)

        # Initially disable editor
        self.set_editor_enabled(False)

        parent_splitter.addWidget(right_panel)

    def load_default_data(self):
        """Load the default skill data"""
        default_data = {
            "skill_id": {
                "display": "",
                "description": ""
            }
        }

        self.skill_data = default_data
        self.refresh_skills_list()

    def refresh_skills_list(self):
        """Refresh the skills list widget"""
        self.skills_list.clear()

        for skill_id in self.skill_data.keys():
            item = QListWidgetItem(skill_id)
            item.setData(Qt.UserRole, skill_id)
            self.skills_list.addItem(item)

        self.count_label.setText(f"{len(self.skill_data)} skills")

    def on_skill_selected(self, item):
        """Handle skill selection from list"""
        skill_id = item.data(Qt.UserRole)
        self.load_skill_to_editor(skill_id)

    def load_skill_to_editor(self, skill_id):
        """Load a skill into the editor"""
        if skill_id in self.skill_data:
            self.current_skill_id = skill_id
            skill = self.skill_data[skill_id]

            # Load data into form
            self.skill_id_input.setText(skill_id)
            self.display_input.setText(skill.get("display", ""))
            self.description_input.setPlainText(skill.get("description", ""))

            # Update editor title
            self.editor_title.setText(f"Editing: {skill_id}")

            # Enable editor
            self.set_editor_enabled(True)

    def set_editor_enabled(self, enabled):
        """Enable or disable the editor"""
        self.skill_id_input.setEnabled(enabled)
        self.display_input.setEnabled(enabled)
        self.description_input.setEnabled(enabled)
        self.apply_button.setEnabled(enabled)
        self.revert_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

        if not enabled:
            self.editor_title.setText("Skill Editor - Select a skill to edit")

    def on_skill_id_changed(self):
        """Handle skill ID changes"""
        if self.current_skill_id:
            new_id = self.skill_id_input.text().strip()
            if new_id and new_id != self.current_skill_id:
                self.editor_title.setText(f"Editing: {new_id} (unsaved changes)")

    def on_field_changed(self):
        """Handle field changes"""
        if self.current_skill_id:
            skill_id = self.skill_id_input.text().strip()
            if skill_id:
                self.editor_title.setText(f"Editing: {skill_id} (unsaved changes)")

    def apply_changes(self):
        """Apply current changes to the skill data"""
        if not self.current_skill_id:
            return

        new_id = self.skill_id_input.text().strip()
        if not new_id:
            QMessageBox.warning(self, "Warning", "Skill ID cannot be empty!")
            return

        # Check if renaming and new ID already exists
        if new_id != self.current_skill_id and new_id in self.skill_data:
            QMessageBox.warning(self, "Warning", f"Skill ID '{new_id}' already exists!")
            return

        # Create new skill data
        new_skill_data = {
            "display": self.display_input.text(),
            "description": self.description_input.toPlainText()
        }

        # Remove old entry if ID changed
        if new_id != self.current_skill_id:
            del self.skill_data[self.current_skill_id]

        # Add/update skill
        self.skill_data[new_id] = new_skill_data
        self.current_skill_id = new_id

        # Refresh UI
        self.refresh_skills_list()
        self.editor_title.setText(f"Editing: {new_id}")

        # Select the current item in list
        for i in range(self.skills_list.count()):
            item = self.skills_list.item(i)
            if item.data(Qt.UserRole) == new_id:
                self.skills_list.setCurrentItem(item)
                break

        QMessageBox.information(self, "Success", "Changes applied successfully!")

    def revert_changes(self):
        """Revert changes to the current skill"""
        if self.current_skill_id:
            reply = QMessageBox.question(
                self, "Revert Changes",
                "Are you sure you want to revert all unsaved changes?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.load_skill_to_editor(self.current_skill_id)

    def create_new_skill(self):
        """Create a new skill"""
        # Find a unique ID
        base_id = "new_skill"
        counter = 1
        new_id = base_id

        while new_id in self.skill_data:
            new_id = f"{base_id}_{counter}"
            counter += 1

        # Add new skill
        self.skill_data[new_id] = {
            "display": "",
            "description": ""
        }

        # Refresh and select new skill
        self.refresh_skills_list()
        self.load_skill_to_editor(new_id)

        # Select in list
        for i in range(self.skills_list.count()):
            item = self.skills_list.item(i)
            if item.data(Qt.UserRole) == new_id:
                self.skills_list.setCurrentItem(item)
                break

    def delete_current_skill(self):
        """Delete the currently selected skill"""
        if not self.current_skill_id:
            return

        reply = QMessageBox.question(
            self, "Delete Skill",
            f"Are you sure you want to delete the skill '{self.current_skill_id}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            del self.skill_data[self.current_skill_id]
            self.current_skill_id = None

            self.refresh_skills_list()
            self.set_editor_enabled(False)

            # Clear form
            self.skill_id_input.clear()
            self.display_input.clear()
            self.description_input.clear()

            QMessageBox.information(self, "Success", "Skill deleted successfully!")

    def save_json(self):
        """Save skill data to JSON file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Skill Definitions", "skill_definitions.json",
                "JSON Files (*.json)"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.skill_data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, "Success", f"Skill definitions saved to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def load_json(self):
        """Load skill data from JSON file"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Skill Definitions", "", "JSON Files (*.json)"
            )

            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.skill_data = data
                self.current_skill_id = None
                self.refresh_skills_list()
                self.set_editor_enabled(False)

                # Clear form
                self.skill_id_input.clear()
                self.display_input.clear()
                self.description_input.clear()

                QMessageBox.information(self, "Success", "Skill definitions loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def preview_json(self):
        """Show preview of current JSON data"""
        try:
            json_text = json.dumps(self.skill_data, indent=2, ensure_ascii=False)

            # Create preview dialog
            msg = QMessageBox()
            msg.setWindowTitle("JSON Preview")
            msg.setText("Preview of your skill definitions:")
            msg.setDetailedText(json_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate preview: {str(e)}")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = SkillDefinitionsEditor()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()