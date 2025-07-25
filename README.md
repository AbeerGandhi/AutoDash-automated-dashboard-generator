# Excel/CSV to Graph Dashboard

This project provides a user-friendly dashboard (`dashboard.html`) for visualizing data from CSV or Excel files. It allows you to generate a variety of industry-standard graphs with customizable axes and export your results as a PDF report.

## Features
- **Upload CSV/Excel**: Supports `.csv`, `.xlsx`, and `.xls` files.
- **Graph Configuration**: Select X and Y axes and graph type (Bar, Line, Pie, Scatter, Area) for each graph.
- **Multiple Graphs**: Add or remove multiple graph configurations as needed.
- **Auto-Generate**: Automatically generate all possible graph combinations for your data.
- **Aggregation**: For Bar, Line, Area, and Pie charts, Y values are summed for each unique X value.
- **Export to PDF**: Download all generated graphs as a single PDF report.

## How It Works

1. **File Upload & Parsing**
   - When you upload a CSV or Excel file, the tool reads the file in your browser using JavaScript.
   - For CSV files, it splits the file into rows and columns, automatically detecting headers and data types (numbers vs. text).
   - For Excel files, you must use a backend or a library like `SheetJS` (not included in this HTML-only version). The current tool is optimized for CSV.

2. **Column Detection**
   - The tool identifies all columns in your data and determines which columns are numeric (for Y-axis selection).
   - All columns are available for X-axis selection, but only numeric columns can be used as Y-axis.

3. **Graph Configuration**
   - You can add multiple graph configurations. For each, you select:
     - X-axis (any column)
     - Y-axis (numeric columns)
     - Graph type (Bar, Line, Pie, Scatter, Area)
   - You can add or remove configurations as needed.
   - The "Auto-Generate All" button creates every possible valid combination of X, Y, and graph type for your data.

4. **Data Aggregation**
   - For Bar, Line, Area, and Pie charts, the tool groups your data by the X-axis value and sums the Y values for each group. This ensures each X value appears only once in the chart.
   - For Scatter plots, all individual data points are shown (no aggregation).

5. **Chart Generation**
   - The tool uses [Chart.js](https://www.chartjs.org/) to render interactive charts in your browser.
   - Each graph configuration is rendered as a separate chart card.

6. **Export to PDF**
   - The tool uses [jsPDF](https://github.com/parallax/jsPDF) to export all generated charts into a single PDF report.
   - Each chart is captured as an image and added to the PDF, along with titles and metadata.

7. **No Server Required**
   - All processing (file reading, parsing, charting, PDF export) is done in your browser. No data is uploaded or sent to a server.

## Code Structure & Logic

Below is a summary of the main code components and their roles in `dashboard.html`:

- **Global Variables**
  - `data`: Holds the parsed data from the uploaded file (array of objects).
  - `columns`: List of all column names.
  - `numericColumns`: List of columns detected as numeric (for Y-axis).
  - `graphConfigs`: Array of graph configuration objects (each with x, y, type).
  - `charts`: Stores Chart.js chart instances for later reference (e.g., for PDF export).

- **File Upload & Parsing**
  - `handleFileUpload(event)`: Triggered when a file is selected. Reads the file and parses it as CSV.
  - `parseCSV(text)`: Converts CSV text into an array of objects, inferring numbers and strings.

- **Column Detection**
  - After parsing, the code determines which columns are numeric by checking the type of the first row's values.

- **Graph Configuration UI**
  - `showGraphConfigTable()`: Initializes the graph configuration table with dropdowns for X, Y, and type.
  - `renderGraphConfigTable()`: Renders the current list of graph configurations as a table with dropdowns and remove buttons.
  - `addGraphConfig()`, `removeGraphConfig(idx)`, `updateGraphConfig(idx, key, value)`: Functions to manage the list of graph configurations.

- **Auto-Generate All**
  - `autoGenerateAll()`: Fills `graphConfigs` with all valid (x, y, type) combinations and triggers rendering.

- **Data Aggregation**
  - `aggregateByX(xKey, yKey)`: Groups data by X and sums Y values for each unique X. Used for Bar, Line, Area, and Pie charts.

- **Chart Rendering**
  - `generateGraphs(configs)`: Loops through each graph config and creates a chart card.
  - `createChart(canvasId, type, xKey, yKey, title)`: Uses Chart.js to render the chart. For Bar, Line, Area, and Pie, uses aggregated data; for Scatter, uses raw data.

- **PDF Export**
  - `generatePDF()`: Uses jsPDF to export all rendered charts as images in a single PDF file, including titles and metadata.

- **Other UI Elements**
  - The HTML and CSS provide a modern, responsive interface for file upload, graph configuration, and chart display.

## How to Use

1. **Open the Dashboard**
   - Open `dashboard.html` in your web browser (no server required).

2. **Upload Your Data**
   - Click the file upload area and select a `.csv`, `.xlsx`, or `.xls` file from your computer.
   - The file will be parsed and columns detected automatically.

3. **Configure Graphs**
   - For each graph you want:
     - Select the X-axis (any column).
     - Select the Y-axis (numeric columns only).
     - Select the graph type (Bar, Line, Pie, Scatter, Area).
     - Click **Add Graph** to add more configurations.
     - Click **Remove** to delete a configuration.
   - Click **Generate Selected** to render the chosen graphs.

4. **Auto-Generate All Graphs**
   - Click **Auto-Generate All** to automatically create all possible combinations of X, Y, and graph type for your data.

5. **Export as PDF**
   - Once graphs are generated, click **Export PDF** to download a report containing all the charts.

## Notes
- **Aggregation**: For Bar, Line, Area, and Pie charts, if the X value repeats (e.g., multiple rows for "Clothing"), the Y values are summed for each unique X.
- **Scatter Plots**: Show all individual data points (no aggregation).
- **No Server Required**: All processing is done in the browser. No installation or backend needed.

## Dependencies
- [Chart.js](https://www.chartjs.org/) (for chart rendering)
- [jsPDF](https://github.com/parallax/jsPDF) (for PDF export)
- Both are loaded via CDN in `dashboard.html`.

## Example Workflow
1. Open `dashboard.html` in your browser.
2. Upload `Orders.csv`.
3. Configure a Bar chart: X = Category, Y = Profit, Type = Bar.
4. Add another graph: X = Region, Y = Sales, Type = Pie.
5. Click **Generate Selected** to view the charts.
6. Click **Export PDF** to download your report.

---

For any issues or feature requests, feel free to update this README or the dashboard code! 