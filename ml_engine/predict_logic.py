import os
import sys
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier

from database import init_db,save_student_assessment,get_student_profile_and_history,toggle_roadmap_milestone,get_platform_analytics

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()

G_P = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'P': 4, 'F': 0}

PILLARS = {
    'coding': ['programming', 'java', 'python', 'data structures', 'node', 'react', 'django', 'prolog', 'lisp', 'pyswip', 'problem solving', 'lab', 'software', 'flutter', 'ui design', 'algorithms'],
    'math': ['calculus', 'matrices', 'differential', 'statistical', 'discrete', 'mathematics', 'probability', 'numerical', 'complex variables', 'stochastic', 'foundations', 'analysis'],
    'hardware': ['electrical', 'electronics', 'devices', 'circuits', 'logic design', 'microprocessor', 'analog', 'signals', 'electromagnetic', 'transmission', 'communication', 'ic applications', 'microcontrollers', 'iot', 'antennas', 'vlsi', 'microwave', 'embedded'],
    'systems': ['database', 'dbms', 'operating systems', 'visualization', 'r programming', 'power bi', 'sql', 'organization', 'architecture', 'network analysis', 'simulation', 'networks', 'cryptography', 'security', 'compiler', 'big data', 'cloud', 'spark', 'information security'],
    'theory': ['economics', 'befa', 'english', 'sensitization', 'constitution', 'ethics', 'management', 'gender', 'skill enhancement', 'induction', 'societal', 'rights', 'intellectual property', 'professional practice'],
    'science': ['chemistry', 'physics', 'environmental', 'geology', 'biology'],
    'design': ['graphics', 'workshop', 'cad', 'cam', 'drawing', 'metrology', 'modelling'],
    'mechanical_core': ['thermodynamics', 'mechanics', 'metallurgy', 'production', 'thermal', 'kinematics', 'machine members', 'heat transfer', 'refrigeration', 'dynamics'],
    'civil_core': ['surveying', 'concrete', 'structural', 'geotechnical', 'transportation', 'hydrology', 'foundation']
}

ROADMAPS = {
    'Full Stack Web Engineer (MERN/Next.js)': [
        "Phase 0: Web Fundamentals & Version Control\n    - HTTP/HTTPS protocols, DNS, and how browsers render HTML/CSS\n    - Git Mastery: Branching, Merging, Rebasing, and GitHub Actions basics\n    - Milestone: Static Web – Deploy a multi-page site using only HTML/CSS and Netlify",
        "Phase 1: Advanced Frontend Mastery\n    - JavaScript ES6+ (Promises, Async/Await, Closures, DOM manipulation)\n    - CSS Architectures: Tailwind CSS, SASS, and Responsive Design (Flex/Grid)\n    - Milestone: Interactive UI – Build a Dynamic Task Dashboard with local storage",
        "Phase 2: Framework Core & State Management\n    - React.js 18/19 or Next.js 15 (App Router, Server Components)\n    - State Management: Zustand, Redux Toolkit, or React Query for data fetching\n    - Milestone: E-commerce UI – Build a full product catalog with filtering and cart logic",
        "Phase 3: Backend Systems & API Design\n    - Node.js (Express) or Python (FastAPI) for scalable server logic\n    - Authentication: JWT, OAuth 2.0, and NextAuth implementation\n    - Milestone: Secure API – Create a User Auth system with role-based access control",
        "Phase 4: Databases & Scaling\n    - PostgreSQL (Relational) with Prisma ORM and MongoDB (NoSQL) with Mongoose\n    - Caching with Redis and Search indexing with Meilisearch\n    - Milestone: Social Media Backend – Design a DB schema for follows, likes, and posts",
        "Phase 5: DevOps & Cloud Architecture\n    - Dockerizing apps and CI/CD pipelines with GitHub Actions\n    - Deploying to AWS (EC2/S3) or Vercel and monitoring with Sentry\n    - Milestone: Live SaaS – Deploy a real-time Chat App with WebSockets and auto-scaling"
    ],
    'Data Scientist & Analytics Lead': [
        "Phase 0: Mathematical Logic & Computing\n    - Linear Algebra (Vectors, Matrices) and Multivariable Calculus\n    - Inferential Statistics: P-values, Hypothesis Testing, and Distributions\n    - Milestone: Math Solver – Use NumPy to solve complex linear equations sets",
        "Phase 1: Data Prep & Python Mastery\n    - Advanced Python (Classes, Iterators) and Jupyter Ecosystem\n    - Pandas & NumPy: Data Cleaning, Pivot Tables, and Handling Missing Data\n    - Milestone: Data Cleaning – Process a messy 50,000-row dataset for analysis",
        "Phase 2: Exploratory Data Analysis & Visualization\n    - Matplotlib, Seaborn, and Plotly for interactive charts\n    - Storytelling with Tableau or Power BI\n    - Milestone: Market Insights – Create a full dashboard for a Retail Sales dataset",
        "Phase 3: Statistical Modeling & ML Core\n    - Regression, Decision Trees, and Random Forests (Scikit-Learn)\n    - Model Evaluation: Cross-validation, AUC-ROC, and F1-score\n    - Milestone: Predictor – Build a Loan Default prediction model with 85%+ accuracy",
        "Phase 4: Big Data & Cloud Analytics\n    - SQL for Data Warehousing (BigQuery/Snowflake)\n    - Apache Airflow for data pipeline orchestration\n    - Milestone: ETL Pipeline – Scrape web data and automate its flow into a SQL warehouse",
        "Phase 5: Business Intelligence & Strategy\n    - KPI Design, A/B Testing, and Stakeholder Reporting\n    - Deploying models via Streamlit or Flask\n    - Milestone: Strategic Report – Present a 90% accuracy churn prediction plan to 'Execs'"
    ],
    'DevOps & Platform Engineer': [
        "Phase 0: Systems & Networking Basics\n    - Computer Architecture, Virtualization, and the OSI Model\n    - Network Protocols: SSH, FTP, HTTP/S, and Load Balancing concepts\n    - Milestone: Network Map – Simulate a secure network with subnets and a firewall",
        "Phase 1: Linux Administration & Shell Scripting\n    - Linux Kernel, File Systems, and Permissions management\n    - Bash/Python scripting for task automation and Cron jobs\n    - Milestone: System Monitor – Script a tool that logs CPU/RAM usage and alerts on high load",
        "Phase 2: Infrastructure as Code (IaC)\n    - Provisioning with Terraform (HCL) and configuration with Ansible/Chef\n    - Immutable Infrastructure and Version Controlled Infra\n    - Milestone: Cloud Spawner – Provision a multi-server AWS environment with one command",
        "Phase 3: Containerization & CI/CD\n    - Docker: Writing Dockerfiles, Compose, and Image Optimization\n    - CI/CD Pipelines: GitHub Actions, Jenkins, or GitLab CI\n    - Milestone: Automated Deploy – Push code to GitHub and have it auto-deploy to a container",
        "Phase 4: Orchestration (Kubernetes)\n    - K8s Objects: Pods, Services, Deployments, and Ingress\n    - Helm Charts for package management and K8s Security\n    - Milestone: Microservices Cluster – Deploy a multi-service app on a local K8s cluster",
        "Phase 5: Observability & Reliability\n    - Monitoring with Prometheus/Grafana and Logging with ELK Stack (Elasticsearch, Logstash, Kibana)\n    - Site Reliability Engineering (SRE) principles: SLIs, SLOs, and Error Budgets\n    - Milestone: Dashboard – Create a live status page for a production-grade application"
    ],
    'Generative AI & LLM Engineer': [
        "Phase 0: Machine Learning Foundations\n    - Probability Theory, Gradient Descent, and Matrix Calculus\n    - Python for AI (NumPy, Scipy) and basic Neural Network theory\n    - Milestone: Single Neuron – Implement a Perceptron from scratch to solve logic gates",
        "Phase 1: NLP & Deep Learning Core\n    - Word Embeddings (Word2Vec) and Sequence models (RNNs, LSTMs)\n    - PyTorch or TensorFlow for building Deep Learning models\n    - Milestone: Text Classifier – Build a sentiment analysis tool for movie reviews",
        "Phase 2: Transformer Architectures\n    - Self-Attention mechanisms, Positional Encoding, and Encoder-Decoder blocks\n    - Understanding BERT (Encoder) and GPT (Decoder) specifics\n    - Milestone: Small GPT – Train a character-level GPT model on Shakespeare's text",
        "Phase 3: LLM Fine-Tuning & PEFT\n    - Parameter Efficient Fine-Tuning (LoRA, QLoRA) and Hugging Face Transformers library\n    - RLHF (Reinforcement Learning from Human Feedback) concepts\n    - Milestone: Niche Chatbot – Fine-tune a Llama-3 model on a specific industry dataset",
        "Phase 4: RAG & Vector Databases\n    - Vector Embeddings and Databases (Pinecone, Milvus, Weaviate)\n    - LangChain or LlamaIndex for document retrieval pipelines\n    - Milestone: PDF Scholar – Build an AI that can answer questions based on a 100-page PDF",
        "Phase 5: LLMOps & Deployment\n    - Model Quantization for edge deployment and serving with vLLM or Ollama\n    - API development with FastAPI and monitoring AI drift\n    - Milestone: AI Product – Deploy a production-ready AI agent with tool-calling capabilities"
    ],
    'VLSI & Chip Design Engineer': [
        "Phase 0: Digital Logic & Hardware Foundations\n    - Boolean Algebra, CMOS Logic, and Combinational/Sequential circuit design\n    - Timing Analysis: Setup time, Hold time, and Clock Skew\n    - Milestone: ALU Design – Design a 4-bit Arithmetic Logic Unit using logic gates",
        "Phase 1: HDL Programming (Verilog/VHDL)\n    - RTL coding for synthesis and writing complex Testbenches\n    - Simulation tools: ModelSim, VCS, or Icarus Verilog\n    - Milestone: Traffic Controller – Program a multi-state traffic light system in Verilog",
        "Phase 2: SystemVerilog & Verification\n    - Object-Oriented Programming in SV and Constrained Random Verification\n    - UVM (Universal Verification Methodology) architecture\n    - Milestone: SV Testbench – Create a randomized verification environment for a FIFO",
        "Phase 3: Logic Synthesis & Physical Design\n    - Synthesis: Converting RTL to Gate-level Netlists using Design Compiler\n    - Physical Design: Floorplanning, Placement, and Routing\n    - Milestone: Gate Netlist – Perform synthesis on an 8-bit processor core",
        "Phase 4: Static Timing Analysis (STA) & Power\n    - Sign-off STA, Parasitic extraction (RC), and Power Analysis\n    - Design Rule Checks (DRC) and Layout vs Schematic (LVS)\n    - Milestone: Timing Closure – Optimize a design to remove all Setup/Hold violations",
        "Phase 5: FPGA & Post-Silicon\n    - Mapping designs to FPGA (Vivado/Quartus) and JTAG debugging\n    - Tape-out process and GDSII generation\n    - Milestone: Chip Prototype – Deploy a custom RISC-V SoC on a Physical FPGA board"
    ],
    'IoT & Robotics Systems Architect': [
        "Phase 0: Electronics & C Programming\n    - Ohm's Law, Circuit analysis, and using Multimeters/Oscilloscopes\n    - Low-level C: Pointers, Bitwise manipulation, and Memory Management\n    - Milestone: Circuit Lab – Build and test a sensor-actuator circuit on a breadboard",
        "Phase 1: Microcontroller Mastery\n    - ARM Cortex-M (STM32) or ESP32 architecture and Register-level programming\n    - Interrupts, Timers, PWM, and DMA (Direct Memory Access)\n    - Milestone: Precision Controller – Program an STM32 to control motor speed via PWM",
        "Phase 2: Communication Protocols\n    - Serial protocols: UART, SPI, I2C, and CAN Bus for automotive/industrial use\n    - Wireless: BLE (Bluetooth Low Energy), Zigbee, and LoRaWAN\n    - Milestone: Protocol Bridge – Create a system where two different MCUs exchange data via SPI",
        "Phase 3: Real-Time Operating Systems (RTOS)\n    - Task Scheduling, Mutexes, Semaphores, and Message Queues in FreeRTOS\n    - Handling concurrency and avoiding deadlocks in hardware\n    - Milestone: Multi-tasking Hub – Build a system that reads 5 sensors simultaneously using RTOS",
        "Phase 4: Robotics Core & ROS\n    - Robot Kinematics (Forward/Inverse) and PID Control theory\n    - ROS2 (Robot Operating System): Nodes, Topics, and Gazebo simulation\n    - Milestone: Autonomous Nav – Simulate a robot avoiding obstacles in a 3D environment",
        "Phase 5: IoT Cloud & Security\n    - MQTT/WebSockets and AWS IoT Core or Azure IoT Hub integration\n    - Secure Boot, Encryption, and OTA (Over-the-Air) updates\n    - Milestone: Smart Grid – Build a cloud-connected energy monitor with a web dashboard"
    ],
    'Robotic Manufacturing & Industry 4.0': [
        "Phase 0: CAD/CAM Fundamentals\n    - 3D Modeling (SolidWorks/Fusion 360) and Engineering Drawings\n    - Geometric Dimensioning and Tolerancing (GD&T)\n    - Milestone: Part Design – Create a 3D assembly of a gearbox with moving constraints",
        "Phase 1: Mechatronics & Sensors\n    - Selection of Sensors (Lidar, Vision, Pressure) and Actuators\n    - Signal Conditioning and Analog-to-Digital Conversion (ADC)\n    - Milestone: Smart Grip – Design a robotic gripper that senses object pressure",
        "Phase 2: Industrial Automation (PLC)\n    - Ladder Logic and Function Block Diagram (FBD) programming\n    - HMI (Human Machine Interface) design for factory control\n    - Milestone: Conveyor Logic – Program a PLC to sort objects by height using sensors",
        "Phase 3: Digital Twin & Simulation\n    - Modeling factory layouts in Siemens NX or AnyLogic\n    - Discrete Event Simulation and Virtual Commissioning\n    - Milestone: Virtual Factory – Create a digital twin of a production line to optimize flow",
        "Phase 4: Additive Manufacturing & CNC\n    - CNC G-code programming and 3D Printing (FDM/SLA) optimization\n    - Design for Manufacturing (DfM) and Assembly (DfA)\n    - Milestone: Rapid Tooling – Manufacture a custom bracket using CNC/3D Printing",
        "Phase 5: Industry 4.0 & Smart Systems\n    - AI-driven Predictive Maintenance and Big Data in manufacturing\n    - Cyber-Physical Systems and Enterprise Resource Planning (ERP) integration\n    - Milestone: Lights-out Cell – Design a fully autonomous manufacturing cell simulation"
    ],
    'Aerospace & Fluid Dynamics Researcher': [
        "Phase 0: Fluid Mechanics & Thermodynamics\n    - Viscosity, Pressure, Bernoulli’s Principle, and Flow Regimes\n    - Laws of Thermodynamics and Heat Transfer (Conduction, Convection, Radiation)\n    - Milestone: Pipe Flow – Calculate pressure drops and flow rates in a complex piping system",
        "Phase 1: Aerodynamics & Airfoil Theory\n    - Lift and Drag coefficients, Boundary Layer theory, and Stall conditions\n    - Supersonic vs Subsonic flow and Shockwave analysis\n    - Milestone: Wing Design – Model a high-lift airfoil and calculate its lift-to-drag ratio",
        "Phase 2: Computational Fluid Dynamics (CFD)\n    - Meshing techniques and solving Navier-Stokes equations numerically\n    - Software: Ansys Fluent, OpenFOAM, or Star-CCM+\n    - Milestone: Aero Simulation – Run a CFD analysis on a car body to reduce air resistance",
        "Phase 3: Propulsion Systems\n    - Gas Turbines, Jet Engines, and Rocket Propulsion (Isp, Thrust equations)\n    - Combustion analysis and Nozzle design\n    - Milestone: Engine Cycle – Design a Brayton cycle for a small-scale turbojet",
        "Phase 4: Aerospace Materials & Structures\n    - Composites, High-temperature alloys, and Fatigue analysis\n    - Finite Element Analysis (FEA) for structural integrity\n    - Milestone: Stress Test – Perform a structural analysis on a fuselage section under load",
        "Phase 5: Orbital Mechanics & Space Systems\n    - Kepler’s Laws, Orbital Maneuvers (Hohmann Transfer), and Satellite subsystems\n    - Space Environment and Thermal Control in vacuum\n    - Milestone: Mission Plan – Calculate the fuel and trajectory required for a Mars orbit"
    ],
    'Smart City & Urban Infrastructure Planner': [
        "Phase 0: Civil Surveying & GIS\n    - Land Surveying with Total Station and Levelling techniques\n    - GIS Data Management: ArcGIS or QGIS for spatial layering\n    - Milestone: District Map – Create a GIS layer map showing utility lines and road networks",
        "Phase 1: Transportation & Traffic Systems\n    - Pavement Design (Flexible/Rigid) and Traffic Flow Theory\n    - Intelligent Transportation Systems (ITS) and Public Transit modeling\n    - Milestone: Junction Optimization – Redesign a busy intersection to reduce wait times",
        "Phase 2: Structural Analysis & BIM\n    - Load analysis (Wind, Seismic, Snow) using STAAD.Pro or ETABS\n    - Building Information Modeling (BIM) with Revit for lifecycle management\n    - Milestone: Bridge Model – Design a pedestrian bridge with full structural calculations",
        "Phase 3: Environmental Engineering & Waste\n    - Water Treatment (WTP) and Sewage (STP) design and Stormwater management\n    - Solid Waste Management and circular economy in cities\n    - Milestone: Smart Water – Design a sensor-based leak detection system for a city block",
        "Phase 4: Geotechnical Engineering\n    - Soil Mechanics, Foundation analysis (Shallow/Deep), and Retaining walls\n    - Slope Stability and Soil Improvement techniques\n    - Milestone: Deep Foundation – Design a pile foundation for a high-rise in coastal soil",
        "Phase 5: Sustainable Urban Planning\n    - Green Building (LEED/GRIHA), Smart Grids, and Urban Zoning laws\n    - Disaster Management and Resilient Infrastructure\n    - Milestone: Eco-City Masterplan – Design a 50-acre carbon-neutral township layout"
    ],
    'Geotechnical & Foundation Expert': [
        "Phase 0: Geology & Soil Physics\n    - Rock mechanics, Soil classification (USCS/IS), and Mineralogy\n    - Groundwater flow and Permeability concepts\n    - Milestone: Soil Profile – Identify and log soil layers from a site borehole report",
        "Phase 1: Advanced Soil Mechanics\n    - Shear Strength (Mohr-Coulomb), Consolidation, and Settlement theory\n    - Effective Stress and Pore Water Pressure analysis\n    - Milestone: Settlement Calc – Predict the 10-year settlement of a heavy industrial tank",
        "Phase 2: Subsurface Exploration\n    - Standard Penetration Test (SPT), CPT, and Geophysical methods\n    - Laboratory testing: Triaxial, Direct Shear, and Atterberg limits\n    - Milestone: Site Investigation – Prepare a comprehensive geotechnical lab test plan",
        "Phase 3: Foundation Design (Deep & Shallow)\n    - Bearing Capacity of Rafts, Footings, and Piles (Static/Dynamic analysis)\n    - Group effect in Piles and Negative Skin Friction\n    - Milestone: Foundation Blueprint – Design a raft foundation for a skyscraper on clay",
        "Phase 4: Earth Structures & Retaining Systems\n    - Lateral Earth Pressure (Rankine/Coulomb) and Design of Retaining Walls\n    - Sheet Piling, Cofferdams, and Soil Nailing\n    - Milestone: Shoring System – Design a 10m deep excavation support for a subway station",
        "Phase 5: Numerical Modeling & Software\n    - PLAXIS 2D/3D or GeoStudio for finite element modeling of soil\n    - Earthquake Geotechnics: Liquefaction analysis and Ground Response\n    - Milestone: Stability Report – Perform a 3D slope stability analysis for a hillside highway"
    ],
    'Quantitative Analyst': [
        "Phase 0: Pure Mathematics Foundations\n    - Advanced Calculus, Linear Algebra, and Discrete Mathematics\n    - Probability Theory: Random Variables, Distributions, and Bayes' Theorem\n    - Milestone: Math Logic – Solve 50 complex probability puzzles using Python",
        "Phase 1: Financial Literacy & Markets\n    - Understanding Assets: Stocks, Bonds, Derivatives, and Options\n    - Financial Statements, Market Microstructure, and Order Books\n    - Milestone: Market Report – Analyze historical volatility for a Top 500 stock",
        "Phase 2: Programming for Finance\n    - Python for Finance: Pandas, NumPy, and Scipy for time-series data\n    - C++ basics for high-frequency trading (HFT) performance concepts\n    - Milestone: Data Fetcher – Build a script to pull live market data via YFinance API",
        "Phase 3: Financial Engineering & Models\n    - Black-Scholes Model, Greeks (Delta, Gamma), and Binomial Trees\n    - Monte Carlo Simulations for risk and pricing\n    - Milestone: Option Pricer – Build a Black-Scholes calculator in Python",
        "Phase 4: Algorithmic Trading & Backtesting\n    - Strategy development: Momentum, Mean Reversion, and Arbitrage\n    - Backtesting frameworks and handling 'Slippage' and 'Transaction Costs'\n    - Milestone: Trading Bot – Backtest a Moving Average strategy on 5 years of data",
        "Phase 5: Risk Management & Quant Research\n    - Value at Risk (VaR), Stress Testing, and Portfolio Optimization\n    - Machine Learning in Finance: Signal detection and Sentiment Analysis\n    - Milestone: Risk Dashboard – Build a VaR model for a multi-asset mock portfolio"
    ]
}

def train_m():
    data = {
        'coding':          [95, 85, 40, 30, 60, 50, 80, 20, 15, 10, 90, 45, 30, 95],
        'math':            [90, 80, 50, 40, 95, 60, 60, 75, 85, 70, 60, 50, 40, 95],
        'hardware':        [20, 30, 95, 85, 40, 30, 30, 20, 10, 10, 25, 90, 40, 20],
        'systems':         [70, 80, 40, 30, 60, 95, 50, 30, 20, 15, 85, 40, 20, 90],
        'theory':          [40, 50, 30, 90, 50, 40, 40, 60, 50, 50, 40, 30, 90, 40],
        'science':         [60, 60, 50, 40, 60, 70, 50, 90, 70, 80, 60, 50, 40, 50],
        'design':          [40, 50, 40, 90, 50, 40, 60, 85, 95, 90, 50, 40, 85, 40],
        'mechanical_core': [10, 10, 30, 10, 10, 10, 10, 95, 10, 10, 10, 20, 10, 10],
        'civil_core':      [10, 10, 10, 10, 10, 10, 10, 10, 95, 90, 10, 10, 10, 10],
        'target': [
            'Generative AI & LLM Engineer',
            'Generative AI & LLM Engineer',
            'IoT & Robotics Systems Architect',
            'DevOps & Platform Engineer',
            'Quantitative Analyst',
            'DevOps & Platform Engineer',
            'Full Stack Web Engineer (MERN/Next.js)',
            'Aerospace & Fluid Dynamics Researcher',
            'Smart City & Urban Infrastructure Planner',
            'Geotechnical & Foundation Expert',
            'Full Stack Web Engineer (MERN/Next.js)',
            'VLSI & Chip Design Engineer',
            'Robotic Manufacturing & Industry 4.0',
            'Data Scientist & Analytics Lead'
        ]
    }
    d = pd.DataFrame(data)
    model = RandomForestClassifier(n_estimators=500, random_state=42)
    model.fit(d.drop('target', axis=1), d['target'])
    return model

GLOBAL_MODEL = train_m()

def predict_career(user_data):
    grades = user_data.get('grades', {})
    pillar_scores = {k: [] for k in PILLARS}

    if not grades:
        return {"error": "No grades provided"}

    for sub, grade in grades.items():
        sub_lower = sub.lower()
        grade_val = int(grade) if str(grade).isdigit() else G_P.get(str(grade), 0)
        score = grade_val * 10

        found = False
        for p_key, keywords in PILLARS.items():
            if any(k in sub_lower for k in keywords):
                pillar_scores[p_key].append(score)
                found = True
                break

        if not found:
            pillar_scores['theory'].append(score)

    final_stats = {}
    for p in PILLARS.keys():
        avg = sum(pillar_scores[p]) / len(pillar_scores[p]) if pillar_scores[p] else 0
        final_stats[p] = round(avg, 2)

    input_features = [final_stats[p] for p in ['coding', 'math', 'hardware', 'systems', 'theory', 'science', 'design', 'mechanical_core', 'civil_core']]
    prediction = GLOBAL_MODEL.predict([input_features])[0]
    return {
        "prediction": prediction,
        "roadmap": ROADMAPS.get(prediction, ["Focus on core engineering fundamentals", "Build a project portfolio"]),
        "pillar_stats": final_stats
    }

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        user_data = request.json or {}
        print(f"Analyzing data for: {user_data.get('branch')}")
        result = predict_career(user_data)

        if "error" in result:
            return jsonify(result), 400

        email = user_data.get("email") or f"student_{int(pd.Timestamp.now().timestamp())}@campus.edu"
        full_name = user_data.get("full_name") or user_data.get("name") or "Student"
        branch = user_data.get("branch") or "Engineering"
        academic_year = user_data.get("academic_year") or user_data.get("year") or "3rd Year"

        assessment_id = None
        try:
            assessment_id = save_student_assessment(
                email=email,
                full_name=full_name,
                branch=branch,
                academic_year=academic_year,
                grades=user_data.get("grades", {}),
                predicted_role=result["prediction"],
                pillar_stats=result["pillar_stats"],
                roadmap=result["roadmap"]
            )
            result["assessment_id"] = assessment_id
            result["email"] = email
        except Exception as db_err:
            print(f"[WARN] Database persistence failed: {db_err}")

        return jsonify(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/student/history', methods=['GET'])
def get_history():
    """Fetches past career assessments and roadmap milestone progress for a student."""
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"status": "error", "error": "email parameter is required"}), 400

        profile = get_student_profile_and_history(email)
        if not profile:
            return jsonify({"status": "error", "error": "Student not found"}), 404

        return jsonify({"status": "success", "data": profile})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/student/milestone/toggle', methods=['POST'])
def toggle_milestone():
    try:
        payload = request.get_json(force=True)
        milestone_id = payload.get("milestone_id")
        is_completed = payload.get("is_completed", True)

        if not milestone_id:
            return jsonify({"status": "error", "error": "milestone_id is required"}), 400

        success = toggle_roadmap_milestone(int(milestone_id), bool(is_completed))
        if success:
            return jsonify({
                "status": "success",
                "message": f"Milestone {milestone_id} marked as {'completed' if is_completed else 'pending'}"
            })
        else:
            return jsonify({"status": "error", "error": "Milestone not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        analytics = get_platform_analytics()
        return jsonify({"status": "success", "data": analytics})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    print("AI ML Engine Online on Port 5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
