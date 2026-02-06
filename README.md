# MSURJ AutoLayout

Every year, the MSURJ editorial board spends hours formatting papers into LaTeX, despite the fact that most of our editors don't know how to use LaTeX. This tool takes a pre-processed `.docx` manuscript and produces an Overleaf-ready folder in the MSURJ LaTeX format. The output is a ZIP file containing the manuscript `.tex`, figures, fonts, the `msurj.cls` file, and a generated `bib.bib` when citations are detected.

The easiest way to use it is through the web app.

**Quick Start (Mac)**

0. Pre-process your manuscript in Word, so it is compatible with the AutoLayout system. Detailed instructions on this are in the works. 

1. Clone or download the repository to your system. Open Terminal and go to the project folder (example path shown):
```bash
cd "/path/to/MSURJ AutoLayout"
```
Example:
```bash
cd "/Users/yavuz/Desktop/MSURJ AutoLayout"
```

2. Install required system tools (one time):
```bash
brew install pandoc ruby
gem install anystyle-cli
```

3. Run the web app:
```bash
chmod +x "/path/to/MSURJ AutoLayout/run_webapp.sh"
"/path/to/MSURJ AutoLayout/run_webapp.sh"
```

4. A browser window should open automatically at:
```
http://127.0.0.1:5000
```

If a browser does not open automatically, paste the URL above into your browser.

**How to Use the App**

1. Drag and drop your pre-processed `.docx` file into the upload area.
2. Fill in the metadata fields.
3. Click **Build ZIP**.
4. Your browser will download a ZIP file. Upload that ZIP to Overleaf for review.

**If AnyStyle Is Not Found**

The app uses AnyStyle to convert the references into a `.bib` file.

If you see an AnyStyle error:
1. Make sure you ran:
```bash
gem install anystyle-cli
```
2. Re-run the app.

If AnyStyle is installed but not found, open the **Optional** section in the app and set the full path to `anystyle`. You can find it with:
```bash
which anystyle
```

**Troubleshooting**

1. **`ModuleNotFoundError: No module named 'processing'`**
   - Run the app from the project root using:
   ```bash
   cd "/path/to/MSURJ AutoLayout"
   python -m webapp.app
   ```

2. **Pandoc not found**
   - Install it:
   ```bash
   brew install pandoc
   ```

3. **AnyStyle error**
   - Install it:
   ```bash
   gem install anystyle-cli
   ```