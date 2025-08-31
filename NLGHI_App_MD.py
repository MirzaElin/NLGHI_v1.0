import sys, os, json, csv, logging, shutil
from datetime import datetime, date
from typing import List, Dict, Any, Tuple


from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QScrollArea, QDateEdit, QDialog, QListWidget, QInputDialog,
    QTextEdit, QTabWidget, QListWidgetItem, QCheckBox, QTreeWidget, QTreeWidgetItem,
    QSplitter, QFileDialog, QShortcut, QGroupBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

DATA_FILE = "nlghi_patient_data.json"
CRED_FILE = "nlghi_credentials.json"
SETTINGS_FILE = "nlghi_settings.json"
AUDIT_LOG = "nlghi_audit.log"

FACTORY_USER = "doctor"
FACTORY_PASS = "1234"

logging.basicConfig(
    filename=AUDIT_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def audit(msg: str):
    logging.info(msg)


DEFAULT_SETTINGS = {
    "theme": "light",
    "auto_backup": True,
    "backup_dir": "backups",
    "backups_to_keep": 10,
    "export_dir": "exports"
}

def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(data: Dict[str, Any]):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

SETTINGS = load_settings()




def load_credentials():
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, "r") as f:
                data = json.load(f)
            return {"username": data.get("username", ""), "password": data.get("password", "")}
        except Exception:
            pass
    return {"username": "", "password": ""}

def save_credentials(username, password):
    with open(CRED_FILE, "w") as f:
        json.dump({"username": username, "password": password}, f, indent=2)

def current_username() -> str:
    c = load_credentials()
    return c["username"] or FACTORY_USER




DOMAIN_LIST = [
    "Cardiovascular", "Respiratory/Cardiopulmonary", "Neurological/Neurodegenerative/Brain Injury",
    "Musculoskeletal/Physical Trauma", "Renal", "Hepatic", "Gastrointestinal", "Dermatologic",
    "Urogenital and Reproductive", "Oncologic", "Hematologic", "Genetic/Hereditary", "Endocrinologic",
    "Immunodeficiency", "Nutritional deficiency", "Autoimmune", "Opthalmic", "Otolaryngologic",
    "Psychiatric/Psychological/Mental/Behavioral", "Oral/Dental",
    "Disability - Physical/Mental/Neurodevelopmental", "Dependence on Supportive Aids", "Social well-being",
    "Economic well-being", "Abuse/Neglect", "Risk factors", "Other"
]


DOMAIN_VALUES = [5,5,5,4,4,4,4,3,3,5,4,1,2,2,2,2,2,2,2,2,1,1,1,5,3,1,1]




class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physician Login")
        self.setGeometry(300, 300, 320, 180)

        layout = QVBoxLayout(self)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.check_login)
        layout.addWidget(login_button)

        creds = load_credentials()
        if (not creds["username"] and not creds["password"]) or \
           (creds["username"] == FACTORY_USER and creds["password"] == FACTORY_PASS):
            hint = QLabel("First run detected — login not required.\nClick Login, then set credentials.")
            hint.setStyleSheet("color: gray; font-size: 12px;")
            layout.addWidget(hint)

    def check_login(self):
        entered_user = self.username_input.text()
        entered_pass = self.password_input.text()
        creds = load_credentials()

        if (not creds["username"] and not creds["password"]) or \
           (creds["username"] == FACTORY_USER and creds["password"] == FACTORY_PASS):
            self.accept()
            return

        if entered_user == creds["username"] and entered_pass == creds["password"]:
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials.")




class ChartWindow(QWidget):
    def __init__(self, matrix, timestamps, title):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1200, 600)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        width_px = max(1600, 140 * max(1, len(timestamps)))
        height_px = max(800, 40 * max(1, len(DOMAIN_LIST)))

        dpi = 100
        fig_w_in = width_px / dpi
        fig_h_in = height_px / dpi

        canvas = FigureCanvas(Figure(figsize=(fig_w_in, fig_h_in), dpi=dpi))
        canvas.setMinimumSize(width_px, height_px)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(canvas)

        container = QWidget()
        container.setLayout(inner_layout)
        container.setMinimumSize(width_px, height_px + 40)

        scroll_area.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        ax = canvas.figure.subplots()
        cax = ax.imshow(matrix, aspect='auto', cmap='YlOrRd', interpolation='nearest')
        ax.set_title(title)
        ax.set_xlabel("Session")
        ax.set_ylabel("Domain")
        ax.set_yticks(np.arange(len(DOMAIN_LIST)))
        ax.set_yticklabels(DOMAIN_LIST)
        ax.set_xticks(np.arange(len(timestamps)))
        ax.set_xticklabels(timestamps, rotation=90)
        canvas.figure.colorbar(cax)
        canvas.draw()




def _make_symptom_lexicon():
    L = {}
    def add(terms, idx): 
        for t in terms: L[t] = [idx]

    add([
        "chest pain","angina","palpitations","tachycardia","bradycardia",
        "shortness of breath on exertion","orthopnea","paroxysmal nocturnal dyspnea",
        "edema legs","leg swelling","syncope","fainting","dyspnea on exertion",
        "hypertension","high blood pressure","bp high","heart failure","cyanosis"
    ], 0)

    add(["cough","productive cough","dry cough","wheeze","wheezing",
         "asthma","breathlessness","shortness of breath","dyspnea",
         "hemoptysis","coughing blood","pneumonia","choking"], 1)

    add(["headache","migraine","dizziness","vertigo","seizure","fits",
         "weakness one side","hemiplegia","stroke","tremor","parkinsonism",
         "confusion","memory loss","mci","dementia","numbness","tingling",
         "loss of consciousness","blackout"], 2)

    add(["joint pain","back pain","knee pain","hip pain","fracture","sprain",
         "muscle weakness","stiffness","falls","gait problem","arthritis",
         "osteoporosis"], 3)

    add(["flank pain","hematuria","blood in urine","urine foamy","edema",
         "reduced urine output","kidney stones","renal colic"], 4)

    add(["jaundice","yellow eyes","hepatitis","liver disease","ascites",
         "abdominal swelling","pruritus","itching","alcohol use"], 5)

    add(["abdominal pain","diarrhea","constipation","vomiting","nausea",
         "blood in stool","melena","hematemesis","acid reflux","heartburn",
         "dysphagia","bloating","ibs"], 6)

    add(["rash","itchy rash","hives","psoriasis","eczema","skin lesion",
         "ulcer","wound","cellulitis"], 7)

    add(["dysuria","painful urination","frequency urination","urgency",
         "urinary incontinence","pelvic pain","vaginal discharge",
         "erectile dysfunction","testicular pain"], 8)

    add(["unintentional weight loss","night sweats","lymph node swelling",
         "mass","lump","fatigue cancer","cachexia"], 9)

    add(["easy bruising","bleeding gums","petechiae","anemia","pallor",
         "thrombosis","clot"], 10)

    add(["family history genetic","known mutation","consanguinity"], 11)

    add(["polyuria","polydipsia","polyphagia","weight gain","weight loss",
         "cold intolerance","heat intolerance","thyroid","diabetes",
         "hyperglycemia","hypoglycemia"], 12)

    add(["recurrent infections","opportunistic infection","low immunity"], 13)

    add(["malnutrition","underweight","scurvy","vitamin deficiency",
         "vitamin d deficiency","b12 deficiency"], 14)

    add(["autoimmune","sle","lupus","sjogren","ra","rheumatoid","vasculitis"], 15)

    add(["blurry vision","double vision","eye pain","red eye","conjunctivitis",
         "glaucoma","cataract","vision loss"], 16)

    add(["ear pain","tinnitus","hearing loss","sore throat","hoarseness",
         "sinusitis","nasal discharge","epistaxis"], 17)

    add(["depression","anxiety","panic attack","hallucinations","delusions",
         "insomnia","addiction","substance use","suicidal ideation"], 18)

    add(["toothache","dental pain","gum swelling","oral ulcer","bad breath"], 19)

    add(["wheelchair","mobility aid","intellectual disability","autism",
         "adhd","developmental delay"], 20)

    add(["walker","cane","oxygen therapy","hearing aid","prosthesis"], 21)

    add(["lonely","isolation","no caregiver","housing instability"], 22)

    add(["financial stress","job loss","low income"], 23)

    add(["neglect","physical abuse","emotional abuse","financial abuse"], 24)

    add(["smoking","alcohol","sedentary","high salt","high sugar","obesity",
         "family history heart","family history stroke"], 25)

    add(["fever","chills","fatigue","malaise","pain","weight change"], 26)

    return L

SYMPTOM_LEXICON = _make_symptom_lexicon()

def analyze_symptoms(text: str) -> Dict[str, Any]:
    s = text.strip().lower()
    hits = []
    votes = {i: 0 for i in range(len(DOMAIN_LIST))}
    for phrase, doms in SYMPTOM_LEXICON.items():
        if phrase in s:
            hits.append(phrase)
            for d in doms:
                votes[d] += 1
    ranked = sorted([(i, c) for i, c in votes.items() if c > 0], key=lambda x: x[1], reverse=True)
    suggestions = [{"domain_index": i, "domain_name": DOMAIN_LIST[i], "votes": c} for i, c in ranked]
    return {"keywords_found": sorted(set(hits)), "suggestions": suggestions}




def read_data() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def write_data(d: Dict[str, Any]):
    
    if SETTINGS.get("auto_backup", True):
        make_backup()
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)
    audit(f"{current_username()} wrote data file ({len(d)} patients).")

def ensure_patient_struct(d: Dict[str, Any], mcp: str, name="", gender=""):
    if mcp not in d:
        d[mcp] = {"name": name, "dob": "", "age": 0, "gender": gender, "records": []}
    p = d[mcp]
    p.setdefault("tags", [])
    p.setdefault("history", [])
    p.setdefault("notes", [])
    p.setdefault("future_refs", [])
    p.setdefault("symptom_snapshots", [])
    p.setdefault("attachments", [])
    return p




def make_backup():
    bdir = SETTINGS.get("backup_dir", "backups")
    os.makedirs(bdir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(bdir, f"patients_{ts}.json")
    if os.path.exists(DATA_FILE):
        shutil.copyfile(DATA_FILE, dst)
        
        keep = int(SETTINGS.get("backups_to_keep", 10))
        files = sorted([os.path.join(bdir, f) for f in os.listdir(bdir) if f.endswith(".json")])
        while len(files) > keep:
            old = files.pop(0)
            try: os.remove(old)
            except Exception: pass
        audit(f"{current_username()} created backup: {dst}")

def list_backups() -> List[str]:
    bdir = SETTINGS.get("backup_dir", "backups")
    if not os.path.exists(bdir): return []
    return sorted([os.path.join(bdir, f) for f in os.listdir(bdir) if f.endswith(".json")])

def restore_backup(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    shutil.copyfile(path, DATA_FILE)
    audit(f"{current_username()} restored backup: {path}")




class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(420, 280)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        
        self.theme_combo = QComboBox(); self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(SETTINGS.get("theme","light"))
        form.addRow("Theme:", self.theme_combo)
        
        self.auto_backup = QCheckBox("Enable automatic backup before writing data")
        self.auto_backup.setChecked(SETTINGS.get("auto_backup", True))
        form.addRow(self.auto_backup)
        
        self.backup_dir = QLineEdit(SETTINGS.get("backup_dir","backups")); form.addRow("Backup folder:", self.backup_dir)
        
        self.keep_spin = QSpinBox(); self.keep_spin.setRange(1, 1000); self.keep_spin.setValue(int(SETTINGS.get("backups_to_keep",10))); form.addRow("Backups to keep:", self.keep_spin)
        
        self.export_dir = QLineEdit(SETTINGS.get("export_dir","exports")); form.addRow("Export folder:", self.export_dir)

        layout.addLayout(form)

        btns = QHBoxLayout()
        save_btn = QPushButton("Save"); save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel"); cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn); btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def save(self):
        SETTINGS["theme"] = self.theme_combo.currentText()
        SETTINGS["auto_backup"] = self.auto_backup.isChecked()
        SETTINGS["backup_dir"] = self.backup_dir.text().strip() or "backups"
        SETTINGS["backups_to_keep"] = int(self.keep_spin.value())
        SETTINGS["export_dir"] = self.export_dir.text().strip() or "exports"
        save_settings(SETTINGS)
        QMessageBox.information(self, "Saved", "Settings saved.")
        self.accept()




class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backups")
        self.resize(600, 400)
        layout = QVBoxLayout(self)

        self.listw = QListWidget()
        layout.addWidget(self.listw)

        btns = QHBoxLayout()
        mk = QPushButton("Make Backup"); mk.clicked.connect(self._make)
        rs = QPushButton("Restore Selected"); rs.clicked.connect(self._restore)
        btns.addWidget(mk); btns.addWidget(rs)
        layout.addLayout(btns)

        self.refresh()

    def refresh(self):
        self.listw.clear()
        for p in list_backups():
            self.listw.addItem(p)

    def _make(self):
        make_backup(); self.refresh(); QMessageBox.information(self, "Backup", "Backup created.")

    def _restore(self):
        item = self.listw.currentItem()
        if not item: QMessageBox.warning(self,"Select","Choose a backup to restore."); return
        path = item.text()
        ok = QMessageBox.question(self, "Confirm", f"Restore backup?\n{path}", QMessageBox.Yes|QMessageBox.No)
        if ok == QMessageBox.Yes:
            restore_backup(path)
            QMessageBox.information(self, "Restored", "Backup restored. Restart app to see changes.")


class DataToolsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Tools — Validation")
        self.resize(800, 500)
        layout = QVBoxLayout(self)

        self.output = QTextEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.output)

        run_btn = QPushButton("Run Validation"); run_btn.clicked.connect(self.run_validation)
        layout.addWidget(run_btn)

        self.run_validation()

    def run_validation(self):
        d = read_data()
        lines = []
        lines.append(f"Patients: {len(d)}")
        issues = 0
        for mcp, p in d.items():
            
            recs = p.get("records", [])
            for idx, r in enumerate(recs):
                imp = r.get("impairments", [])
                dsav = r.get("dsavs", [])
                if len(imp) != len(DOMAIN_LIST):
                    issues += 1; lines.append(f"[{mcp}] record {idx}: impairments len={len(imp)} != {len(DOMAIN_LIST)}")
                if len(dsav) != len(DOMAIN_LIST):
                    issues += 1; lines.append(f"[{mcp}] record {idx}: dsavs len={len(dsav)} != {len(DOMAIN_LIST)}")
                
                try:
                    recompute = round(sum([int(imp[i]) * DOMAIN_VALUES[i] for i in range(len(DOMAIN_LIST))]) / 27, 4)
                    if abs(float(r.get("ghi", 0)) - recompute) > 1e-6:
                        issues += 1; lines.append(f"[{mcp}] record {idx}: GHI mismatch {r.get('ghi')} vs {recompute}")
                except Exception:
                    issues += 1; lines.append(f"[{mcp}] record {idx}: error recomputing GHI")

        lines.append(f"Issues found: {issues}")
        self.output.setPlainText("\n".join(lines))


class ReportBuilderDialog(QDialog):
    def __init__(self, parent_app, mcp):
        super().__init__(parent_app)
        self.app = parent_app; self.mcp = mcp
        self.setWindowTitle(f"Report Builder — MCP {mcp}")
        self.resize(820, 600)
        layout = QVBoxLayout(self)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

        btns = QHBoxLayout()
        gen_visit = QPushButton("Generate Latest Visit Summary"); gen_visit.clicked.connect(self.gen_visit)
        gen_all = QPushButton("Generate Lifetime Summary"); gen_all.clicked.connect(self.gen_all)
        exp_txt = QPushButton("Export as .txt"); exp_txt.clicked.connect(lambda: self.export("txt"))
        exp_md = QPushButton("Export as .md"); exp_md.clicked.connect(lambda: self.export("md"))
        exp_csv = QPushButton("Export records as .csv"); exp_csv.clicked.connect(self.export_csv)
        btns.addWidget(gen_visit); btns.addWidget(gen_all); btns.addWidget(exp_txt); btns.addWidget(exp_md); btns.addWidget(exp_csv)
        layout.addLayout(btns)

        self.gen_visit()

    def _patient(self):
        d = read_data(); return d.get(self.mcp, {})

    def gen_visit(self):
        p = self._patient()
        name = p.get("name",""); gender = p.get("gender",""); dob = p.get("dob","")
        recs = p.get("records", [])
        last = recs[-1] if recs else {}
        ghi = last.get("ghi","N/A"); date_s = last.get("session_date","N/A")
        lines = [
            f"# Visit Summary — MCP {self.mcp}",
            f"Name: {name}   Gender: {gender}   DOB: {dob}",
            f"Session Date: {date_s}",
            f"GHI: {ghi}",
            "",
            "## DSAV (per domain)",
        ]
        dsav = last.get("dsavs", [])
        for i, val in enumerate(dsav):
            lines.append(f"- {DOMAIN_LIST[i]}: {val}")
        self.summary_text.setPlainText("\n".join(lines))

    def gen_all(self):
        p = self._patient()
        lines = [f"# Lifetime Summary — MCP {self.mcp}", f"Name: {p.get('name','')}  Gender: {p.get('gender','')}  DOB: {p.get('dob','')}", ""]
        # notes
        if p.get("history"):
            lines.append("## History entries"); 
            for h in p["history"]:
                lines.append(f"- {h.get('timestamp','')}: {h.get('title','')}")
        if p.get("notes"):
            lines.append("\n## Doctor's notes")
            for n in p["notes"]:
                lines.append(f"- {n.get('timestamp','')}: {n.get('title','')} (attach_latest={n.get('attach_latest',False)})")
        if p.get("future_refs"):
            lines.append("\n## Future references")
            for r in p["future_refs"]:
                lines.append(f"- {r.get('due','')}: {r.get('title','')}  [{'DONE' if r.get('done') else 'PENDING'}]")
        
        if p.get("records"):
            lines.append("\n## Records (GHI by session)")
            for r in p["records"]:
                lines.append(f"- {r.get('session_date','')}: GHI={r.get('ghi','N/A')}")

        self.summary_text.setPlainText("\n".join(lines))

    def export(self, ext: str):
        os.makedirs(SETTINGS.get("export_dir","exports"), exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "Save report as", os.path.join(SETTINGS.get("export_dir","exports"), f"report_{self.mcp}.{ext}"), f"*.{ext}")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.summary_text.toPlainText())
        QMessageBox.information(self, "Exported", f"Saved to {path}")

    def export_csv(self):
        p = self._patient()
        recs = p.get("records", [])
        if not recs:
            QMessageBox.information(self, "No data", "No records to export.")
            return
        os.makedirs(SETTINGS.get("export_dir","exports"), exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "Save records CSV", os.path.join(SETTINGS.get("export_dir","exports"), f"records_{self.mcp}.csv"), "CSV Files (*.csv)")
        if not path: return
        fieldnames = ["timestamp","session_date","ghi"] + [f"dsav_{i}" for i in range(len(DOMAIN_LIST))]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
            for r in recs:
                row = {"timestamp": r.get("timestamp",""), "session_date": r.get("session_date",""), "ghi": r.get("ghi","")}
                dsav = r.get("dsavs", [])
                for i in range(len(DOMAIN_LIST)):
                    row[f"dsav_{i}"] = dsav[i] if i < len(dsav) else ""
                w.writerow(row)
        QMessageBox.information(self, "Exported", f"Saved to {path}")



class TimelineDialog(QDialog):
    def __init__(self, parent_app, mcp):
        super().__init__(parent_app)
        self.mcp = mcp; self.setWindowTitle(f"Timeline — MCP {mcp}"); self.resize(900, 600)
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget(); self.tree.setHeaderLabels(["When", "Type", "Title/Detail"])
        layout.addWidget(self.tree)

        btns = QHBoxLayout()
        exp = QPushButton("Export Timeline (.md)"); exp.clicked.connect(self.export_md)
        btns.addWidget(exp)
        layout.addLayout(btns)

        self.populate()

    def _patient(self):
        return read_data().get(self.mcp, {})

    def populate(self):
        self.tree.clear()
        p = self._patient()
        events = []  
        for r in p.get("records", []):
            events.append((r.get("session_date",""), "Visit", f"GHI={r.get('ghi','N/A')}"))
        for h in p.get("history", []):
            events.append((h.get("timestamp",""), "History", h.get("title","")))
        for n in p.get("notes", []):
            events.append((n.get("timestamp",""), "Note", n.get("title","")))
        for fr in p.get("future_refs", []):
            mark = "DONE" if fr.get("done") else "PENDING"
            events.append((fr.get("due",""), "Future", f"{mark}: {fr.get('title','')}"))
        
        events.sort(key=lambda x: x[0])
        for when, typ, txt in events:
            item = QTreeWidgetItem([when, typ, txt])
            self.tree.addTopLevelItem(item)

    def export_md(self):
        p = self._patient()
        os.makedirs(SETTINGS.get("export_dir","exports"), exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(self, "Save timeline", os.path.join(SETTINGS.get("export_dir","exports"), f"timeline_{self.mcp}.md"), "Markdown (*.md)")
        if not path: return
        lines = [f"# Timeline — MCP {self.mcp}", f"Name: {p.get('name','')}  Gender: {p.get('gender','')}  DOB: {p.get('dob','')}", ""]
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            lines.append(f"- {item.text(0)} — **{item.text(1)}** — {item.text(2)}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        QMessageBox.information(self, "Exported", f"Saved to {path}")


class PatientWorkspaceDialog(QDialog):
    def __init__(self, parent_app, mcp):
        super().__init__(parent_app)
        self.app = parent_app; self.mcp = mcp
        self.setWindowTitle(f"Patient Workspace — MCP: {mcp}")
        self.resize(980, 720)

        self.tabs = QTabWidget(self)
        self._build_history_tab()
        self._build_symptom_tab()
        self._build_notes_tab()
        self._build_future_ref_tab()
        self._build_attachments_tab()

        root = QVBoxLayout(self); root.addWidget(self.tabs)
        self._load_all_sections()

    
    def _read(self): return read_data()
    def _write(self, d): write_data(d)
    def _ensure(self, d): return ensure_patient_struct(d, self.mcp)

    
    def _build_history_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        form = QHBoxLayout()
        self.hist_title = QLineEdit(); self.hist_title.setPlaceholderText("History entry title")
        form.addWidget(self.hist_title)
        addb = QPushButton("Add Entry"); addb.clicked.connect(self._add_history_entry); form.addWidget(addb)
        lay.addLayout(form)
        self.hist_text = QTextEdit(); self.hist_text.setPlaceholderText("Write patient history here..."); self.hist_text.setAcceptRichText(False); lay.addWidget(self.hist_text)
        self.hist_list = QListWidget(); self.hist_list.itemClicked.connect(self._load_history_entry)
        lay.addWidget(QLabel("Existing history entries:")); lay.addWidget(self.hist_list)
        btns = QHBoxLayout()
        ub = QPushButton("Update Selected"); ub.clicked.connect(self._update_history_entry)
        db = QPushButton("Delete Selected"); db.clicked.connect(self._delete_history_entry)
        eb = QPushButton("Export Selected (.txt)"); eb.clicked.connect(self._export_history_txt)
        btns.addWidget(ub); btns.addWidget(db); btns.addWidget(eb); lay.addLayout(btns)
        self.tabs.addTab(w, "History")

    def _load_all_history(self):
        self.hist_list.clear(); d = self._read(); p = d.get(self.mcp, {})
        for idx, e in enumerate(p.get("history", [])):
            item = QListWidgetItem(f"{idx+1}. {e.get('title','(untitled)')} — {e.get('timestamp','')}"); item.setData(Qt.UserRole, idx); self.hist_list.addItem(item)

    def _add_history_entry(self):
        t = self.hist_title.text().strip() or "(untitled)"; b = self.hist_text.toPlainText().strip()
        if not b: QMessageBox.warning(self,"Missing","Write some history text first."); return
        d = self._read(); p = self._ensure(d); p["history"].append({"title": t, "body": b, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._write(d); QMessageBox.information(self,"Saved","History entry added."); self.hist_title.clear(); self.hist_text.clear(); self._load_all_history()

    def _load_history_entry(self, item):
        idx = item.data(Qt.UserRole); d = self._read(); p = d.get(self.mcp, {}); L = p.get("history", [])
        if 0 <= idx < len(L): e = L[idx]; self.hist_title.setText(e.get("title","")); self.hist_text.setPlainText(e.get("body",""))

    def _update_history_entry(self):
        it = self.hist_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an entry to update."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["history"]):
            p["history"][idx]["title"] = self.hist_title.text().strip() or "(untitled)"
            p["history"][idx]["body"] = self.hist_text.toPlainText().strip()
            p["history"][idx]["edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._write(d); QMessageBox.information(self,"Updated","History updated."); self._load_all_history()

    def _delete_history_entry(self):
        it = self.hist_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an entry to delete."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["history"]): del p["history"][idx]; self._write(d); QMessageBox.information(self,"Deleted","Entry removed."); self._load_all_history()

    def _export_history_txt(self):
        it = self.hist_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an entry to export."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d); e = p.get("history", [])[idx]
        path, _ = QFileDialog.getSaveFileName(self, "Save history", f"history_{self.mcp}_{idx+1}.txt", "Text Files (*.txt)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Title: {e.get('title','')}\nTimestamp: {e.get('timestamp','')}\nEdited: {e.get('edited_at','')}\n\n{e.get('body','')}")
        QMessageBox.information(self,"Exported",f"Saved to {path}")

    
    def _build_symptom_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.addWidget(QLabel("Enter symptoms in natural language (advisory only)."))
        self.sym_input = QTextEdit(); self.sym_input.setPlaceholderText("e.g., 'Shortness of breath and chest pain on exertion.'"); self.sym_input.setAcceptRichText(False); lay.addWidget(self.sym_input)
        b = QHBoxLayout(); ab = QPushButton("Analyze"); ab.clicked.connect(self._run_symptom_check); sb = QPushButton("Save Snapshot"); sb.clicked.connect(self._save_symptom_snapshot)
        b.addWidget(ab); b.addWidget(sb); lay.addLayout(b)
        split = QSplitter(Qt.Horizontal)
        left = QWidget(); ll = QVBoxLayout(left); ll.addWidget(QLabel("Matched keywords:")); self.sym_keywords = QListWidget(); ll.addWidget(self.sym_keywords)
        right = QWidget(); rl = QVBoxLayout(right); rl.addWidget(QLabel("Suggested domains: (votes)")); self.sym_domains = QTreeWidget(); self.sym_domains.setHeaderLabels(["Domain","Votes"]); rl.addWidget(self.sym_domains)
        split.addWidget(left); split.addWidget(right); lay.addWidget(split)
        self.sym_snap_list = QListWidget(); lay.addWidget(QLabel("Previous symptom snapshots:")); lay.addWidget(self.sym_snap_list)
        loadb = QPushButton("Load Selected"); loadb.clicked.connect(self._load_symptom_snapshot); lay.addWidget(loadb)
        self.tabs.addTab(w, "Symptom Checker")

    def _run_symptom_check(self):
        tx = self.sym_input.toPlainText()
        if not tx.strip(): QMessageBox.warning(self,"Empty","Enter symptoms first."); return
        res = analyze_symptoms(tx); self._render_symptom_result(res)

    def _render_symptom_result(self, res):
        self.sym_keywords.clear(); [self.sym_keywords.addItem(k) for k in res["keywords_found"]]
        self.sym_domains.clear()
        for s in res["suggestions"]:
            item = QTreeWidgetItem([s["domain_name"], str(s["votes"])]); item.setData(0, Qt.UserRole, s["domain_index"]); self.sym_domains.addTopLevelItem(item)

    def _save_symptom_snapshot(self):
        tx = self.sym_input.toPlainText().strip()
        if not tx: QMessageBox.warning(self,"Empty","Nothing to save."); return
        res = analyze_symptoms(tx); d = self._read(); p = self._ensure(d); p["symptom_snapshots"].append({"text": tx, "result": res, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._write(d); QMessageBox.information(self,"Saved","Snapshot saved."); self._load_symptom_snapshots()

    def _load_symptom_snapshot(self):
        it = self.sym_snap_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose a snapshot."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d); snaps = p.get("symptom_snapshots", [])
        if 0 <= idx < len(snaps): s = snaps[idx]; self.sym_input.setPlainText(s.get("text","")); self._render_symptom_result(s.get("result", {"keywords_found":[], "suggestions":[]}))

    def _load_symptom_snapshots(self):
        self.sym_snap_list.clear(); d = self._read(); p = self._ensure(d)
        for i, s in enumerate(p.get("symptom_snapshots", [])):
            it = QListWidgetItem(f"{i+1}. {s.get('timestamp','')} — {len(s.get('result',{}).get('keywords_found',[]))} keywords"); it.setData(Qt.UserRole, i); self.sym_snap_list.addItem(it)

    
    def _build_notes_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        form = QHBoxLayout()
        self.note_title = QLineEdit(); self.note_title.setPlaceholderText("Note title"); form.addWidget(self.note_title)
        self.note_attach_latest = QCheckBox("Attach to latest visit (if any)"); form.addWidget(self.note_attach_latest)
        lay.addLayout(form)
        self.note_text = QTextEdit(); self.note_text.setPlaceholderText("Write clinical note here (advisory only)."); self.note_text.setAcceptRichText(False); lay.addWidget(self.note_text)
        btns = QHBoxLayout()
        addb = QPushButton("Add Note"); addb.clicked.connect(self._add_note)
        upb = QPushButton("Update Selected"); upb.clicked.connect(self._update_note)
        delb = QPushButton("Delete Selected"); delb.clicked.connect(self._delete_note)
        btns.addWidget(addb); btns.addWidget(upb); btns.addWidget(delb); lay.addLayout(btns)
        self.note_list = QListWidget(); self.note_list.itemClicked.connect(self._load_note); lay.addWidget(QLabel("Notes:")); lay.addWidget(self.note_list)
        self.tabs.addTab(w, "Doctor's Notes")

    def _load_all_notes(self):
        self.note_list.clear(); d = self._read(); p = self._ensure(d)
        for idx, n in enumerate(p.get("notes", [])):
            lbl = f"{idx+1}. {n.get('timestamp','')} — {n.get('title','(untitled)')}"
            if n.get("attach_latest", False): lbl += "  [attached to latest visit]"
            it = QListWidgetItem(lbl); it.setData(Qt.UserRole, idx); self.note_list.addItem(it)

    def _add_note(self):
        t = self.note_title.text().strip() or "(untitled)"; b = self.note_text.toPlainText().strip()
        if not b: QMessageBox.warning(self,"Missing","Write note text first."); return
        d = self._read(); p = self._ensure(d); attach = self.note_attach_latest.isChecked(); context_session_date = None
        recs = p.get("records", [])
        if attach and recs: context_session_date = recs[-1].get("session_date")
        p["notes"].append({"title": t, "body": b, "attach_latest": attach, "context_session_date": context_session_date, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._write(d); QMessageBox.information(self,"Saved","Note added."); self.note_title.clear(); self.note_text.clear(); self._load_all_notes()

    def _load_note(self, item):
        idx = item.data(Qt.UserRole); d = self._read(); p = self._ensure(d); L = p.get("notes", [])
        if 0 <= idx < len(L): n = L[idx]; self.note_title.setText(n.get("title","")); self.note_text.setPlainText(n.get("body","")); self.note_attach_latest.setChecked(bool(n.get("attach_latest",False)))

    def _update_note(self):
        it = self.note_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose a note to update."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["notes"]):
            n = p["notes"][idx]; n["title"] = self.note_title.text().strip() or "(untitled)"; n["body"] = self.note_text.toPlainText().strip()
            n["attach_latest"] = self.note_attach_latest.isChecked(); n["edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._write(d); QMessageBox.information(self,"Updated","Note updated."); self._load_all_notes()

    def _delete_note(self):
        it = self.note_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose a note to delete."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["notes"]): del p["notes"][idx]; self._write(d); QMessageBox.information(self,"Deleted","Note removed."); self._load_all_notes()

    
    def _build_future_ref_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        row = QHBoxLayout()
        self.fr_title = QLineEdit(); self.fr_title.setPlaceholderText("Follow-up / reference title"); row.addWidget(self.fr_title)
        self.fr_due = QDateEdit(); self.fr_due.setCalendarPopup(True); self.fr_due.setDisplayFormat("yyyy-MM-dd")
        row.addWidget(QLabel("Due date:")); row.addWidget(self.fr_due); lay.addLayout(row)
        self.fr_text = QTextEdit(); self.fr_text.setPlaceholderText("Optional details / instructions..."); self.fr_text.setAcceptRichText(False); lay.addWidget(self.fr_text)
        btns = QHBoxLayout()
        addb = QPushButton("Add"); addb.clicked.connect(self._add_future_ref)
        doneb = QPushButton("Mark Selected Done"); doneb.clicked.connect(self._mark_future_ref_done)
        delb = QPushButton("Delete Selected"); delb.clicked.connect(self._delete_future_ref)
        btns.addWidget(addb); btns.addWidget(doneb); btns.addWidget(delb); lay.addLayout(btns)
        self.fr_list = QListWidget(); self.fr_list.itemClicked.connect(self._load_future_ref); lay.addWidget(QLabel("Future references:")); lay.addWidget(self.fr_list)
        self.tabs.addTab(w, "Future References")

    def _load_all_future_refs(self):
        self.fr_list.clear(); d = self._read(); p = self._ensure(d)
        for idx, r in enumerate(p.get("future_refs", [])):
            status = "DONE" if r.get("done", False) else "PENDING"; due = r.get("due",""); title = r.get("title","(untitled)")
            it = QListWidgetItem(f"{idx+1}. [{status}] {due} — {title}"); it.setData(Qt.UserRole, idx); self.fr_list.addItem(it)

    def _add_future_ref(self):
        t = self.fr_title.text().strip() or "(untitled)"; details = self.fr_text.toPlainText().strip(); due = self.fr_due.date().toString("yyyy-MM-dd")
        d = self._read(); p = self._ensure(d); p["future_refs"].append({"title": t, "details": details, "due": due, "done": False, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._write(d); QMessageBox.information(self,"Saved","Future reference added."); self.fr_title.clear(); self.fr_text.clear(); self._load_all_future_refs()

    def _load_future_ref(self, item):
        idx = item.data(Qt.UserRole); d = self._read(); p = self._ensure(d); L = p.get("future_refs", [])
        if 0 <= idx < len(L):
            r = L[idx]; self.fr_title.setText(r.get("title","")); self.fr_text.setPlainText(r.get("details",""))
            try:
                y,m,d0 = map(int, r.get("due","1970-01-01").split("-")); self.fr_due.setDate(date(y,m,d0))
            except Exception: pass

    def _mark_future_ref_done(self):
        it = self.fr_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an item."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["future_refs"]):
            p["future_refs"][idx]["done"] = True; p["future_refs"][idx]["done_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._write(d); QMessageBox.information(self,"Updated","Marked as done."); self._load_all_future_refs()

    def _delete_future_ref(self):
        it = self.fr_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an item to delete."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["future_refs"]): del p["future_refs"][idx]; self._write(d); QMessageBox.information(self,"Deleted","Removed."); self._load_all_future_refs()

    
    def _build_attachments_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        btns = QHBoxLayout()
        addb = QPushButton("Add Attachment"); addb.clicked.connect(self._add_attachment)
        openb = QPushButton("Open Selected"); openb.clicked.connect(self._open_attachment)
        delb = QPushButton("Delete Selected"); delb.clicked.connect(self._delete_attachment)
        btns.addWidget(addb); btns.addWidget(openb); btns.addWidget(delb); lay.addLayout(btns)
        self.att_list = QListWidget(); lay.addWidget(self.att_list)
        self.tabs.addTab(w, "Attachments")

    def _load_all_attachments(self):
        self.att_list.clear(); d = self._read(); p = self._ensure(d)
        for idx, a in enumerate(p.get("attachments", [])):
            it = QListWidgetItem(f"{idx+1}. {a.get('path','')} — {a.get('desc','')} ({a.get('timestamp','')})"); it.setData(Qt.UserRole, idx); self.att_list.addItem(it)

    def _add_attachment(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file to attach")
        if not path: return
        desc, ok = QInputDialog.getText(self, "Describe", "Short description:")
        if not ok: return
        d = self._read(); p = self._ensure(d); p["attachments"].append({"path": path, "desc": desc, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._write(d); self._load_all_attachments()

    def _open_attachment(self):
        it = self.att_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an attachment."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d); L = p.get("attachments", [])
        if 0 <= idx < len(L):
            path = L[idx].get("path","")
            if not os.path.exists(path):
                QMessageBox.warning(self,"Missing","File not found on disk."); return
            
            try:
                if sys.platform.startswith("win"): os.startfile(path)  
                elif sys.platform == "darwin": os.system(f"open '{path}'")
                else: os.system(f"xdg-open '{path}'")
            except Exception as e:
                QMessageBox.warning(self,"Error", str(e))

    def _delete_attachment(self):
        it = self.att_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose an attachment to delete."); return
        idx = it.data(Qt.UserRole); d = self._read(); p = self._ensure(d)
        if 0 <= idx < len(p["attachments"]): del p["attachments"][idx]; self._write(d); self._load_all_attachments()

    
    def _load_all_sections(self):
        self._load_all_history(); self._load_all_notes(); self._load_all_future_refs(); self._load_symptom_snapshots(); self._load_all_attachments()




class NLGHIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NLGHI v1.0 - Newfoundland and Labrador Geriatric Health Index")
        self.setGeometry(100, 100, 1300, 850)
        self.setStyleSheet("font-size: 14px;")
        self.data = {}
        self.chart_window = None
        self.fig_window = None
        self._build_ui()
        self.maybe_first_time_setup()
        self._install_shortcuts()

    
    def _build_ui(self):
        layout = QVBoxLayout()

        header = QLabel("NLGHI v1.0 - Newfoundland and Labrador Geriatric Health Index")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header, alignment=Qt.AlignCenter)

        branding = QLabel("© 2025 Mirza Niaz Zaman Elin. All rights reserved.")
        branding.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(branding, alignment=Qt.AlignCenter)

        
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Search patients by MCP, name, or tag (live)")
        self.search_input.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search_input)

        top = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Patient Registry"))
        self.patient_list = QListWidget()
        self.patient_list.itemClicked.connect(self.load_patient_record)
        left_col.addWidget(self.patient_list)

        
        tag_box = QGroupBox("Tags for selected patient")
        tag_lay = QHBoxLayout(tag_box)
        self.tag_input = QLineEdit(); self.tag_input.setPlaceholderText("Comma-separated tags, e.g., 'frailty, diabetes'")
        save_tags = QPushButton("Save Tags"); save_tags.clicked.connect(self._save_tags)
        tag_lay.addWidget(self.tag_input); tag_lay.addWidget(save_tags)
        left_col.addWidget(tag_box)

        top.addLayout(left_col, stretch=1)

        
        form = QVBoxLayout()
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Patient Name:")); self.name_input = QLineEdit(); r1.addWidget(self.name_input)
        r1.addWidget(QLabel("MCP:")); self.mcp_input = QLineEdit(); r1.addWidget(self.mcp_input)
        form.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("DOB:")); self.dob_input = QDateEdit(); self.dob_input.setCalendarPopup(True); self.dob_input.setDisplayFormat("yyyy-MM-dd"); r2.addWidget(self.dob_input)
        r2.addWidget(QLabel("Gender:")); self.gender_input = QComboBox(); self.gender_input.addItems(["Male","Female","Other"]); r2.addWidget(self.gender_input)
        form.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Session Date:")); self.session_date_input = QDateEdit(); self.session_date_input.setCalendarPopup(True); self.session_date_input.setDisplayFormat("yyyy-MM-dd"); r3.addWidget(self.session_date_input)
        form.addLayout(r3)

        
        severity_items = ["0","1","2","3","4","5"]
        self.domain_dropdowns = []
        for dname in DOMAIN_LIST:
            h = QHBoxLayout()
            label = QLabel(dname + " (0=None, 1=Suspected/Undiagnosed, 2=Diagnosed but Mild, 3=Diagnosed and Moderate, 4=Diagnosed and Severe, 5=Diagnosed and Critical)")
            combo = QComboBox(); combo.addItems(severity_items); self.domain_dropdowns.append(combo)
            h.addWidget(label, stretch=3); h.addWidget(combo, stretch=1); form.addLayout(h)

        self.save_button = QPushButton("Save Visit and Calculate GHI"); self.save_button.clicked.connect(self.save_record); form.addWidget(self.save_button)
        self.result_label = QLabel("GHI: N/A"); form.addWidget(self.result_label, alignment=Qt.AlignCenter)

        btns = QHBoxLayout()
        b1 = QPushButton("View GHI Trend"); b1.clicked.connect(self.view_ghi_chart); btns.addWidget(b1)
        b2 = QPushButton("View DSAV Trend"); b2.clicked.connect(self.view_dsav_chart); btns.addWidget(b2)
        b3 = QPushButton("Change Credentials"); b3.clicked.connect(self.change_credentials); btns.addWidget(b3)
        b4 = QPushButton("Delete Selected Patient"); b4.clicked.connect(self.delete_selected_patient); btns.addWidget(b4)
        
        wb = QPushButton("Open Patient Workspace"); wb.clicked.connect(self.open_patient_workspace); btns.addWidget(wb)
        tl = QPushButton("Timeline"); tl.clicked.connect(self.open_timeline); btns.addWidget(tl)
        rb = QPushButton("Report Builder"); rb.clicked.connect(self.open_report_builder); btns.addWidget(rb)
        st = QPushButton("Settings"); st.clicked.connect(self.open_settings); btns.addWidget(st)
        bk = QPushButton("Backups"); bk.clicked.connect(self.open_backups); btns.addWidget(bk)
        dt = QPushButton("Data Tools"); dt.clicked.connect(self.open_data_tools); btns.addWidget(dt)

        form.addLayout(btns)

        top.addLayout(form, stretch=3)
        layout.addLayout(top)
        
        content = QWidget()
        content.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(content)
        outer = QVBoxLayout()
        outer.addWidget(scroll)
        self.setLayout(outer)

        self.load_patient_registry()

    
    def _install_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_record)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search_input.setFocus())
        QShortcut(QKeySequence("F2"), self, activated=self.open_patient_workspace)
        QShortcut(QKeySequence("F3"), self, activated=self.open_timeline)
        QShortcut(QKeySequence("F4"), self, activated=self.open_report_builder)

    
    def _apply_filter(self):
        q = self.search_input.text().strip().lower()
        self.patient_list.clear()
        d = read_data()
        for mcp, p in d.items():
            name = p.get("name","").lower()
            tags = ",".join(p.get("tags",[])).lower()
            if (q in mcp.lower()) or (q in name) or (q and q in tags) or (q == ""):
                self.patient_list.addItem(mcp)

    def _save_tags(self):
        it = self.patient_list.currentItem()
        if not it: QMessageBox.warning(self,"Select","Choose a patient first."); return
        mcp = it.text()
        d = read_data(); p = ensure_patient_struct(d, mcp)
        tags = [t.strip() for t in self.tag_input.text().split(",") if t.strip()]
        p["tags"] = sorted(set(tags))
        write_data(d); QMessageBox.information(self,"Saved","Tags updated.")
        self._apply_filter()

    
    def maybe_first_time_setup(self):
        creds = load_credentials()
        first_run = (not creds["username"] and not creds["password"]) or (creds["username"] == FACTORY_USER and creds["password"] == FACTORY_PASS)
        if first_run:
            resp = QMessageBox.question(self, "First-time Setup", "No secure credentials are set yet.\n\nSet a username & password now?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                username, ok1 = QInputDialog.getText(self, "Set Username", "New username:")
                if not ok1 or not username.strip():
                    QMessageBox.warning(self, "Skipped", "Username not set. You can set credentials later from 'Change Credentials'."); return
                password, ok2 = QInputDialog.getText(self, "Set Password", "New password:")
                if not ok2 or not password:
                    QMessageBox.warning(self, "Skipped", "Password not set. You can set credentials later from 'Change Credentials'."); return
                save_credentials(username.strip(), password); QMessageBox.information(self, "Saved", "Credentials saved. Next time, login will be required.")
        
        if SETTINGS.get("theme") == "dark":
            self.setStyleSheet(self.styleSheet() + "\nQWidget{background:#1e1f22;color:#e5e5e5;} QPushButton{background:#2b2d31;border:1px solid #3a3d41;}")

    
    def load_patient_registry(self):
        self.data = read_data()
        self.patient_list.clear()
        for mcp in self.data:
            self.patient_list.addItem(mcp)

    def load_patient_record(self, item):
        mcp = item.text()
        patient = self.data.get(mcp, {})
        if patient:
            self.name_input.setText(patient.get("name", ""))
            self.mcp_input.setText(mcp)
            try:
                self.dob_input.setDate(date.fromisoformat(patient.get("dob")))
            except Exception:
                pass
            self.gender_input.setCurrentText(patient.get("gender", ""))
            self.tag_input.setText(", ".join(patient.get("tags", [])))

    def delete_selected_patient(self):
        selected_item = self.patient_list.currentItem()
        if selected_item:
            mcp = selected_item.text()
            confirm = QMessageBox.question(self, "Delete Patient", f"Are you sure you want to delete patient {mcp}?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.data.pop(mcp, None); write_data(self.data); self.load_patient_registry()

    
    def change_credentials(self):
        username, ok1 = QInputDialog.getText(self, "Change Username", "New username:")
        if ok1 and username.strip():
            password, ok2 = QInputDialog.getText(self, "Change Password", "New password:")
            if ok2 and password:
                save_credentials(username.strip(), password); QMessageBox.information(self, "Updated", "Credentials updated successfully.\nThey will be required next time.")

    
    def save_record(self):
        try:
            name = self.name_input.text().strip()
            mcp = self.mcp_input.text().strip()
            dob = self.dob_input.date().toPyDate()
            gender = self.gender_input.currentText()
            session_date = self.session_date_input.date().toPyDate()
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))

            impairments = [int(d.currentText()) for d in self.domain_dropdowns]
            dsavs = [imp * val for imp, val in zip(impairments, DOMAIN_VALUES)]
            ghi = round(sum(dsavs) / 27, 4)

            record = {"timestamp": today, "session_date": str(session_date), "impairments": impairments, "dsavs": dsavs, "ghi": ghi}

            self.data = read_data()
            if mcp not in self.data:
                self.data[mcp] = {"name": name, "dob": str(dob), "age": age, "gender": gender, "records": []}
            self.data[mcp]["records"].append(record)
            write_data(self.data)

            self.result_label.setText(f"GHI: {ghi}")
            QMessageBox.information(self, "Saved", "Patient visit saved and GHI calculated.")
            audit(f"{current_username()} saved record for MCP={mcp}")
            self.load_patient_registry()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    
    def _line_chart(self, timestamps, values, title, ylabel):
        self.fig_window = QWidget(); self.fig_window.setWindowTitle(title)
        scroll = QScrollArea(self.fig_window); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn); scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        container = QWidget(); v = QVBoxLayout(container); canvas = FigureCanvas(Figure(figsize=(14, 6))); v.addWidget(canvas)
        scroll.setWidget(container); main_layout = QVBoxLayout(); main_layout.addWidget(scroll); self.fig_window.setLayout(main_layout)
        ax = canvas.figure.subplots(); ax.plot(timestamps, values, marker='o', linestyle='-'); ax.set_title(title); ax.set_xlabel("Session Date"); ax.set_ylabel(ylabel); ax.grid(True); canvas.draw()
        self.fig_window.show()

    def load_chart(self, key, ylabel, title, do_sum=False):
        mcp = self.mcp_input.text().strip()
        if not mcp or not os.path.exists(DATA_FILE):
            QMessageBox.warning(self, "Invalid MCP", "Please enter a valid MCP number to view chart.")
            return
        self.data = read_data()
        if mcp not in self.data or not self.data[mcp]["records"]:
            QMessageBox.information(self, "No Records", "No visits found for this patient.")
            return
        records = self.data[mcp]["records"]; timestamps = [r["session_date"] for r in records]
        values = []
        for r in records:
            if key not in r: values.append(None)
            elif do_sum and isinstance(r[key], list): values.append(sum(r[key]))
            else: values.append(r[key])
        filtered_timestamps, filtered_values = [], []
        for t, v in zip(timestamps, values):
            if v is not None:
                filtered_timestamps.append(t)
                try: filtered_values.append(float(v))
                except Exception: filtered_values.append(np.nan)
        if not filtered_values:
            QMessageBox.information(self, "No Data", "No valid data points available to plot."); return
        self._line_chart(filtered_timestamps, filtered_values, title, ylabel)

    def view_ghi_chart(self):
        self.load_chart("ghi", "GHI", "GHI Over Time")

    def view_dsav_chart(self):
        mcp = self.mcp_input.text().strip()
        if not mcp or not os.path.exists(DATA_FILE):
            QMessageBox.warning(self, "Invalid MCP", "Please enter a valid MCP number to view chart.")
            return
        self.data = read_data()
        if mcp not in self.data or not self.data[mcp]["records"]:
            QMessageBox.information(self, "No Records", "No visits found for this patient.")
            return
        records = self.data[mcp]["records"]
        timestamps = [r["session_date"] for r in records]
        domain_count = len(DOMAIN_LIST)
        session_count = len(records)
        matrix = np.zeros((domain_count, session_count))
        for j, r in enumerate(records):
            dsavs = r.get("dsavs", [])
            for i in range(domain_count):
                matrix[i][j] = dsavs[i] if i < len(dsavs) else 0
        self.chart_window = ChartWindow(matrix, timestamps, "DSAV Heatmap by Domain and Session")
        self.chart_window.show()

    
    def open_patient_workspace(self):
        mcp = self.mcp_input.text().strip()
        if not mcp: QMessageBox.warning(self, "MCP required", "Enter an MCP to open the workspace."); return
        d = read_data(); ensure_patient_struct(d, mcp, self.name_input.text().strip(), self.gender_input.currentText()); write_data(d)
        PatientWorkspaceDialog(self, mcp).exec_()

    def open_timeline(self):
        mcp = self.mcp_input.text().strip()
        if not mcp: QMessageBox.warning(self, "MCP required", "Enter an MCP to open Timeline."); return
        TimelineDialog(self, mcp).exec_()

    def open_report_builder(self):
        mcp = self.mcp_input.text().strip()
        if not mcp: QMessageBox.warning(self, "MCP required", "Enter an MCP to open Report Builder."); return
        ReportBuilderDialog(self, mcp).exec_()

    def open_settings(self):
        SettingsDialog(self).exec_()

    def open_backups(self):
        BackupDialog(self).exec_()

    def open_data_tools(self):
        DataToolsDialog(self).exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = NLGHIApp()
        window.show()
        sys.exit(app.exec_())
