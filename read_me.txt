1️⃣ Open Terminal in the Project Folder
Open Command Prompt or PowerShell.

Run:
cd "C:\Users\PaulChelotiMulongo\Documents\Projects\football_tipster"


2️⃣ Create a Python Virtual Environment (Recommended)
Run:
python -m venv venv

Activate it:
venv\Scripts\activate

ERROR: Activate.ps1 cannot be loaded
Solution - Run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

venv\Scripts\Activate.ps1

You should now see:
(venv) C:\Users\PaulChelotiMulongo\Documents\Projects\football_tipster>

3️⃣ Install Dependencies
Run:
pip install -r requirements.txt


4️⃣ Run the Project
Now run:
python main.py


python -m tipster.generate_tips

python -m tipster.validate_tips