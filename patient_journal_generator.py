import random
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

class PatientJournalGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_style = ParagraphStyle(
            'CustomStyle',
            parent=self.styles['Normal'],
            spaceBefore=10,
            spaceAfter=10,
            fontSize=10,
            leading=14,
        )
        
        # Common medical conditions and treatments in Norwegian
        self.conditions = [
            "Høyt blodtrykk", "Type 2 Diabetes", "Øvre luftveisinfeksjon",
            "Angstlidelse", "Korsryggsmerter", "Sesongallergier",
            "Migrene", "Gastritt", "Bronkitt", "Artritt"
        ]
        
        self.treatments = [
            "Forskrevet medisiner", "Fysioterapi",
            "Anbefalt livsstilsendringer", "Regelmessig oppfølging",
            "Kostholdsendringer", "Treningsprogram", "Samtaleterapi",
            "Blodprøver", "Bildediagnostikk", "Henvisning til spesialist"
        ]

    def generate_visit_history(self, start_date, num_years):
        visits = []
        current_date = start_date
        end_date = start_date + timedelta(days=365 * num_years)
        
        while current_date < end_date:
            # Generate 3-8 visits per year
            yearly_visits = random.randint(3, 8)
            for _ in range(yearly_visits):
                visit_date = current_date + timedelta(days=random.randint(0, 365))
                if visit_date < end_date:
                    condition = random.choice(self.conditions)
                    treatment = random.choice(self.treatments)
                    vital_signs = {
                        "BP": f"{random.randint(110, 140)}/{random.randint(60, 90)}",
                        "HR": f"{random.randint(60, 100)}",
                        "Temp": f"{round(random.uniform(36.1, 37.5), 1)}°C"
                    }
                    visits.append({
                        "date": visit_date,
                        "condition": condition,
                        "treatment": treatment,
                        "vital_signs": vital_signs,
                        "notes": f"Pasienten presenterte med {condition.lower()}. {treatment} ble iverksatt."
                    })
            current_date += timedelta(days=365)
        
        return sorted(visits, key=lambda x: x["date"])

    def create_patient_journal(self, patient_data, output_path):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Add patient information in Norwegian
        story.append(Paragraph(f"Medisinsk Journal", self.styles["Title"]))
        story.append(Spacer(1, 20))
        
        # Patient details in Norwegian
        patient_info = [
            f"Navn: {patient_data['name']}",
            f"Fødselsdato: {patient_data['dob']}",
            f"Pasient-ID: {patient_data['id']}",
            f"Kjønn: {patient_data['gender']}",
            f"Blodtype: {patient_data['blood_type']}"
        ]
        
        for info in patient_info:
            story.append(Paragraph(info, self.custom_style))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("Besøkshistorikk", self.styles["Heading1"]))
        story.append(Spacer(1, 10))
        
        # Generate visit history with Norwegian text
        start_date = datetime.now() - timedelta(days=365 * patient_data['history_years'])
        visits = self.generate_visit_history(start_date, patient_data['history_years'])
        
        for visit in visits:
            visit_date = visit["date"].strftime("%Y-%m-%d")
            story.append(Paragraph(f"Besøksdato: {visit_date}", self.styles["Heading2"]))
            story.append(Paragraph(f"Tilstand: {visit['condition']}", self.custom_style))
            story.append(Paragraph(f"Behandling: {visit['treatment']}", self.custom_style))
            story.append(Paragraph(f"Vitale tegn:", self.custom_style))
            story.append(Paragraph(f"  - Blodtrykk: {visit['vital_signs']['BP']}", self.custom_style))
            story.append(Paragraph(f"  - Hjertefrekvens: {visit['vital_signs']['HR']} slag/min", self.custom_style))
            story.append(Paragraph(f"  - Temperatur: {visit['vital_signs']['Temp']}", self.custom_style))
            story.append(Paragraph(f"Notater: Pasienten presenterte med {visit['condition'].lower()}. {visit['treatment']} ble iverksatt.", self.custom_style))
            story.append(Spacer(1, 10))
        
        doc.build(story)

def main():
    # Create output directory if it doesn't exist
    output_dir = "data/generated_journals"
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample patient data with Norwegian gender
    patient_data = {
        "name": "Ole Hansen",
        "dob": "1980-05-15",
        "id": "19800515-1234",
        "gender": "Mann",
        "blood_type": "A+",
        "history_years": 10
    }
    
    generator = PatientJournalGenerator()
    output_path = os.path.join(output_dir, f"{patient_data['name']} - {patient_data['id']}.pdf")
    generator.create_patient_journal(patient_data, output_path)
    print(f"Pasientjournal generert: {output_path}")

if __name__ == "__main__":
    main() 