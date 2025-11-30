# Unique School Timetable System

A smart and automated school timetable generator designed to reduce manual scheduling efforts.  
This system uses **Genetic Algorithms (GA)** to automatically generate conflict-free timetables for schools, ensuring optimal allocation of teachers, classes, subjects, and time slots.

---

## 🚀 Features

- Fully automated timetable generation  
- Genetic Algorithm–based optimization  
- Avoids teacher/time conflicts  
- Ensures each class gets required subjects  
- Supports custom constraints (period limits, breaks, etc.)  
- User-friendly and modular code structure  
- Easily customizable for any school model  

---

## 🧬 How the Genetic Algorithm Works

This project applies a **Genetic Algorithm (GA)** to optimize school timetables through:

### **1. Population Initialization**
A random set of possible timetable solutions is generated.

### **2. Fitness Evaluation**
Each timetable is checked for:
- Teacher conflicts  
- Class conflicts  
- Missing subject periods  
- Invalid room/time assignments  

A higher fitness score means a better timetable.

### **3. Selection**
Best timetables are selected for reproduction based on fitness.

### **4. Crossover**
Two good timetables mix to create new child timetables.

### **5. Mutation**
Random swaps in subjects, teachers, or timeslots increase diversity.

### **6. Termination**
GA stops when:
- A conflict-free timetable is found  
- Or max iterations are reached  

---

## 🏗️ Project Structure


unique-school-timetable-system/
│── data/
│── src/
│ ├── timetable.py
│ ├── genetic_algorithm.py
│ ├── fitness.py
│ ├── utils.py
│ └── main.py
│── output/
│── README.md
│── requirements.txt



---

## ⚙️ Technologies Used

- Python  
- Genetic Algorithms  
- Object-Oriented Programming  
- CSV / JSON data management  

---

## 📦 Installation

```bash
git clone https://github.com/PrathameshBansode/unique-school-timetable-system
cd unique-school-timetable-system
pip install -r requirements.txt


python src/main.py


📚 Use Cases

School timetable scheduling

Coaching class scheduling

College scheduling (with modifications)

Automated resource allocation systems

🤝 Contributing

Pull requests are welcome!
Feel free to fork, improve the genetic algorithm, or add your own constraints.

📄 License

This project is open-source and free to use under the MIT License.
