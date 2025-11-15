# Laboratorio 9

### **Instalar dependencias**
python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt


### **Pruebas de Conexión**

Test-NetConnection -ComputerName iot.redesuvg.cloud -Port 9092


### **Enviar lecturas (Producer)**
python .\producer.py --topic 22764-22249 
- Por defecto se usa iot.redesuvg.cloud:9092.
- Para forzar otra dirección: --bootstrap 147.182.219.133:9092 
- Para modo compacto: --mode compact

### **Consumir logs (Consumer)**

python .\consumer.py --topic 22764-22249

### **Gráfico**

python .\consumer_plot.py --topic 22764-22249