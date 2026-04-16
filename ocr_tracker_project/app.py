from flask import Flask, render_template, request, redirect
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

# 🔥 LOAD GOOGLE SHEET
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1tL9A4Va25v-O2gLNl_fCgkxCCWV3yZm9DXdsinUEnlg/gviz/tq?tqx=out:csv&sheet=DATA"
    
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)

    return df


@app.route('/', methods=['GET', 'POST'])
def tracker():
    message = None

    if request.method == 'POST':
        plate_input = request.form.get('plate')
        engine_input = request.form.get('engine')

        df = load_data()

        # 🔥 CLEAN COLUMN NAMES
        df.columns = df.columns.str.strip().str.lower()

        # 🔥 ENSURE REQUIRED COLUMNS
        if 'engine' not in df.columns or 'plate' not in df.columns:
            return render_template('tracker.html', message="Column missing")

        # 🔥 CLEAN DATA
        df['engine'] = df['engine'].astype(str).str.strip()
        df['plate'] = df['plate'].astype(str).str.strip().str.upper()

        # 🔥 ORCR SEARCH
        if engine_input:
            engine_clean = ''.join(filter(str.isdigit, engine_input))[-4:]

            # SEARCH ENGINE
            engine_match = df[df['engine'].str.contains(engine_clean, na=False)]

            # SEARCH SINSKI
            sinski_match = pd.DataFrame()
            if 'sinski' in df.columns:
                sinski_match = df[df['sinski'].astype(str).str.contains(engine_clean, na=False)]

            # LOGIC
            if not sinski_match.empty:
                message = "Transfer of Ownership is still in process. Please contact our office for updates."

            elif not engine_match.empty:
                return redirect('/success?type=orcr')

            else:
                message = "Not Available"

        # 🔥 PLATE SEARCH
        elif plate_input:
            plate_clean = plate_input.strip().upper()

            result = df[df['plate'].str.contains(plate_clean, na=False)]

            if not result.empty:
                return redirect('/success?type=plate')
            else:
                message = "Not Available"

    return render_template('tracker.html', message=message)


@app.route('/success')
def success():
    from flask import request

    search_type = request.args.get('type')

    if search_type == 'orcr':
        title = "ORCR AVAILABLE"
    else:
        title = "PLATE AVAILABLE"

    return render_template('success.html', title=title)


if __name__ == '__main__':
    app.run(debug=True)
