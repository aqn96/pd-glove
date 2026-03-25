# Images Directory

This directory contains images referenced in the documentation.

## Organization

```
images/
├── hardware/          # Photos of physical hardware (glove, sensors, Pi setup)
├── results/           # Plots, graphs, DSP outputs
├── architecture/      # System diagrams, wiring diagrams
└── README.md
```

## Adding Images to Markdown

### Method 1: Local File Reference (Recommended for Committed Images)

1. Add your image file to this directory (e.g., `docs/images/hardware/glove-mounted.jpg`)
2. Reference it in markdown:

```markdown
![Glove with mounted sensors](images/hardware/glove-mounted.jpg)
```

Or with relative path from docs/:
```markdown
![Glove with mounted sensors](./images/hardware/glove-mounted.jpg)
```

### Method 2: GitHub UI Drag-and-Drop (Quick but creates issue references)

1. Edit your `.md` file directly on GitHub web interface
2. Drag and drop image into the text editor
3. GitHub auto-uploads to their CDN and generates markdown:
   ```markdown
   ![image](https://github.com/user-attachments/assets/xxxxx.png)
   ```

**Note:** This method stores images in GitHub's asset hosting, not in your repo.

### Method 3: Commit Images First (Best Practice)

```bash
# On local machine
cd pd-glove/docs/images/hardware
# Copy your image
cp ~/Pictures/glove-photo.jpg ./glove-mounted.jpg

# Stage and commit
git add glove-mounted.jpg
git commit -m "Add photo of mounted glove hardware"
git push

# Then reference in any .md file:
![Mounted glove](images/hardware/glove-mounted.jpg)
```

## Image Guidelines

- **Format:** Use `.jpg` for photos, `.png` for screenshots/diagrams
- **Size:** Keep under 2MB per image (resize if needed)
- **Naming:** Use descriptive kebab-case names (e.g., `pla-ring-hot-glue-mount.jpg`)
- **Alt text:** Always include descriptive alt text for accessibility

## Example Usage in validation-results.md

```markdown
## Hardware Mounting Solution

![PLA ring with hot glue mounting](images/hardware/pla-ring-mount.jpg)

The sensors are mounted using PLA rings with hot glue applied to the side-top bars.
```
