from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import pandas as pd
from werkzeug.utils import secure_filename
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'dashboard_generator/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Parse file
        try:
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(filepath, encoding='latin1')
            else:
                df = pd.read_excel(filepath)
        except Exception as e:
            return jsonify({'error': f'Failed to parse file: {str(e)}'}), 400
        columns = list(df.columns)
        numeric_columns = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
        return jsonify({
            'columns': columns,
            'numeric_columns': numeric_columns,
            'filename': filename
        })
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/aggregate', methods=['POST'])
def aggregate():
    data = request.json
    filename = data.get('filename')
    x = data.get('x')
    y = data.get('y')
    chart_type = data.get('type')
    z = data.get('z')  # for heatmap, bubble, etc.
    stack_col = data.get('stack_col')  # for stacked charts
    hierarchy = data.get('hierarchy')  # for treemap/sunburst
    start_col = data.get('start')  # for gantt
    end_col = data.get('end')      # for gantt
    size_col = data.get('size')    # for bubble
    bins = data.get('bins', 10)    # for histogram
    if not filename or not chart_type:
        return jsonify({'error': 'Missing parameters'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 400
    # Aggregation logic
    try:
        if chart_type in ['bar', 'line', 'area', 'pie', 'donut']:
            if not x or not y:
                return jsonify({'error': 'Missing x or y'}), 400
            grouped = df.groupby(x)[y].sum().reset_index()
            labels = grouped[x].astype(str).tolist()
            values = grouped[y].tolist()
            return jsonify({'labels': labels, 'values': values})
        elif chart_type == 'scatter':
            if not x or not y:
                return jsonify({'error': 'Missing x or y'}), 400
            points = df[[x, y]].dropna()
            data_points = points.to_dict(orient='records')
            return jsonify({'points': data_points})
        elif chart_type == 'heatmap':
            if not x or not y or not z:
                return jsonify({'error': 'Missing x, y, or z'}), 400
            grouped = df.groupby([x, y])[z].sum().reset_index()
            x_labels = grouped[x].astype(str).unique().tolist()
            y_labels = grouped[y].astype(str).unique().tolist()
            matrix = []
            for y_val in y_labels:
                row = []
                for x_val in x_labels:
                    match = grouped[(grouped[x]==x_val) & (grouped[y]==y_val)]
                    row.append(match[z].values[0] if not match.empty else 0)
                matrix.append(row)
            return jsonify({'x_labels': x_labels, 'y_labels': y_labels, 'matrix': matrix})
        elif chart_type == 'histogram':
            if not y:
                return jsonify({'error': 'Missing y'}), 400
            counts, bin_edges = np.histogram(df[y].dropna(), bins=bins)
            bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]
            return jsonify({'labels': bin_labels, 'values': counts.tolist()})
        elif chart_type in ['boxplot', 'violin']:
            if not x or not y:
                return jsonify({'error': 'Missing x or y'}), 400
            groups = df.groupby(x)[y]
            stats = []
            for name, group in groups:
                vals = group.dropna().values
                if len(vals) == 0:
                    continue
                q1 = np.percentile(vals, 25)
                med = np.percentile(vals, 50)
                q3 = np.percentile(vals, 75)
                minv = np.min(vals)
                maxv = np.max(vals)
                outliers = vals[(vals < q1 - 1.5*(q3-q1)) | (vals > q3 + 1.5*(q3-q1))].tolist()
                stats.append({
                    'label': str(name),
                    'min': minv,
                    'q1': q1,
                    'median': med,
                    'q3': q3,
                    'max': maxv,
                    'outliers': outliers,
                    'values': vals.tolist() if chart_type == 'violin' else None
                })
            return jsonify({'stats': stats})
        elif chart_type == 'bubble':
            if not x or not y or not size_col:
                return jsonify({'error': 'Missing x, y, or size'}), 400
            points = df[[x, y, size_col]].dropna()
            data_points = points.rename(columns={size_col: 'size'}).to_dict(orient='records')
            return jsonify({'points': data_points})
        elif chart_type == 'radar':
            if not x or not y:
                return jsonify({'error': 'Missing x or y'}), 400
            grouped = df.groupby(x)[y].mean().reset_index()
            labels = grouped[x].astype(str).tolist()
            values = grouped[y].tolist()
            return jsonify({'labels': labels, 'values': values})
        elif chart_type in ['stacked_bar', 'stacked_area']:
            if not x or not y or not stack_col:
                return jsonify({'error': 'Missing x, y, or stack_col'}), 400
            grouped = df.groupby([x, stack_col])[y].sum().reset_index()
            x_labels = grouped[x].astype(str).unique().tolist()
            stack_labels = grouped[stack_col].astype(str).unique().tolist()
            data = {label: [0]*len(x_labels) for label in stack_labels}
            for i, row in grouped.iterrows():
                xi = x_labels.index(str(row[x]))
                si = str(row[stack_col])
                data[si][xi] = row[y]
            return jsonify({'x_labels': x_labels, 'stack_labels': stack_labels, 'data': data})
        elif chart_type == 'gantt':
            if not x or not start_col or not end_col:
                return jsonify({'error': 'Missing task, start, or end column'}), 400
            tasks = df[[x, start_col, end_col]].dropna()
            data_points = tasks.rename(columns={x: 'task', start_col: 'start', end_col: 'end'}).to_dict(orient='records')
            return jsonify({'tasks': data_points})
        elif chart_type == 'waterfall':
            if not x or not y:
                return jsonify({'error': 'Missing x or y'}), 400
            ordered = df[[x, y]].dropna().sort_values(x)
            labels = ordered[x].astype(str).tolist()
            values = ordered[y].tolist()
            cumulative = np.cumsum(values).tolist()
            return jsonify({'labels': labels, 'values': values, 'cumulative': cumulative})
        elif chart_type in ['treemap', 'sunburst']:
            if not hierarchy or not y:
                return jsonify({'error': 'Missing hierarchy or y'}), 400
            grouped = df.groupby(hierarchy)[y].sum().reset_index()
            # Return as list of dicts for frontend to build hierarchy
            data_points = grouped.to_dict(orient='records')
            return jsonify({'points': data_points, 'hierarchy': hierarchy, 'value': y})
        else:
            return jsonify({'error': 'Unknown chart type'}), 400
    except Exception as e:
        return jsonify({'error': f'Aggregation error: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True) 