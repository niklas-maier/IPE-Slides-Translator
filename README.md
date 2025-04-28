# Make script runable

## 0. Install OpenAI

Install the OpenAI package into your Python environment:

```bash
pip install openai
```

## 1. Insert API key in `translate_workflow.py`

In the `main` function of `translate_workflow.py`, place your ChatGPT API key in the call to `translate_slides_range()`.

---

# Actual Workflow

1. **Load the original slide deck into Ipe**

2. **Export as `.xml`**

   In Ipe, click:

   ```
   File > Save As
   ```

   Then save the file using the `.xml` format. This will create a `.ipe` file.

3. **Repeat for all slides**

   Save each slide individually and name them like so:

   ```
   slide08.ipe
   slide09.ipe
   ...
   ```

4. **Run the Python function**

   Use the `translate_workflow` module and tell the program which slide decks to translate:

   ```python
   translate_slides_range(8, 14, api_key="your-api-key")
   ```

5. **Load the merged slides in Ipe**

   Open the resulting file:

   ```
   slidesXX_merged.ipe
   ```

6. **Export as PDF**

   In Ipe:

   ```
   File > Save As
   ```

   Then save the file as a `.pdf`.

---

# Problems

The automatic translation process sometimes introduces formatting issues. These need to be corrected manually. When loading a broken slide into Ipe, the program will usually display the LaTeX error and indicate where the issue is. Below are the most common errors encountered so far, along with explanations and how to fix them.

---

## 1. Unescaped `#` character

**Example error message:**

```
! You can't use `macro parameter character #' in restricted horizontal mode.
l.1082 ...the tree corresponds to the worst-case #
```

**What this means:**

The `#` character was not escaped in the translated output. LaTeX interprets `#` as a special character and will throw an error if it's used without escaping.

**How to fix it:**

1. Open the corresponding `slidesXX_merged.ipe` file.
2. Search for the problematic text — in this case:

   ```
   the tree corresponds to the worst-case #comparisons%
   ```

3. Manually replace the `#` with `\#`, like so:

   ```
   the tree corresponds to the worst-case \#comparisons%
   ```

---

## 2. Extra `}` or unmatched `$`

**Example error message:**

```
! Extra }, or forgotten $.
l.1137 \iperesetcolor}
```

**What this means:**

During translation, an uneven number of `{` or `$` symbols may have been introduced. This leads to LaTeX parsing errors.

**How to fix it:**

1. Check the file `slidesXX_extracted.log` to find the line number where the error occurs.
2. Use that information to locate the corresponding tag in `slidesXX_extracted.txt`.
3. Review the original string and compare it to the translated result in `slidesXX_merged.ipe`.
4. Adjust the formatting by balancing all `{`, `}`, and `$` symbols appropriately.

---

## 3. Missing `$` inserted (Math environment issue)

**Example error message:**

```
Missing $ inserted.
<inserted text> 
                $
l.1286 $D - d $\geq 2$$%
```

**What this means:**

The translated text accidentally introduced or removed math mode delimiters (`$`). This can result in double dollar signs, partially opened math environments, or similar syntax problems.

**How to fix it:**

1. Open `slidesXX_extracted_translated.txt` and search for the LaTeX snippet shown in the error (e.g. `D - d $\geq 2$$%`).
2. Identify which tag this translated string belongs to.
3. Use that tag to look up the corresponding original string in `slidesXX_extracted.txt`.
4. Open `slidesXX_merged.ipe`, find the tag, and manually fix the math formatting by ensuring:
   - All math expressions are enclosed by matching `$...$`.
   - No extra or duplicated `$` signs are present.

---


## 4. Misaligned Highlighted Text Due to Changed Word Lengths

**What this means:**

When text is highlighted (e.g., using `\highlight` or similar markup), the translated version may differ in word length compared to the original. This can cause the highlighted area to no longer align properly with the visual structure of the slide. For example, the highlighted box may become too short, too long, or shift out of place entirely.

**Why it happens:**

Highlighting in Ipe is often position-dependent. Since the translation can introduce longer or shorter words, especially when switching languages, the positioning of text and highlights can become desynchronized.

**How to fix it:**

1. Open the affected slide in `slidesXX_merged.ipe`.
2. Visually inspect any highlighted regions, especially where text has been translated and formatting changed.
3. If the highlight appears misaligned:
   - Manually adjust the position or size of the highlight object.
   - Alternatively, reposition the text or reduce line breaks to better fit within the original highlight box.
4. Use Ipe’s graphical interface to drag and resize the highlight area as needed for a clean fit.

> **Note:** This type of formatting issue typically won’t generate a LaTeX error — it’s a purely visual alignment problem that must be corrected by hand during final review.



# Methods for Running

## `translate_ipe_file(file, batch_size=BATCHSIZE, max_elements=MAXELEMENTS, api_key=APIKEY)`

- `file`: Path to the `.xml` file to translate.
- `batch_size`: Number of text elements sent per API request (suggested: 100).
- `max_elements`: Optional limit for number of elements (good for debugging).
- `api_key`: Your ChatGPT API key.

## `translate_slides_range(start_slide, end_slide, batch_size=..., max_elements=..., api_key=...)`

Calls `translate_ipe_file()` on slides from `start_slide` to `end_slide` (inclusive). Example:

```python
translate_slides_range(5, 18, batch_size=100, api_key="your-api-key")
```

## Debug mode

To preview translations without sending API requests:

```python
translate_slides_range(5, 18, batch_size=50, debug_mode=True)
```
