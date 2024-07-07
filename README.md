<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<h3 align="center">Composing Program PDF</h3>

<!-- ABOUT THE PROJECT -->
## About The Project

This is python script that converts the composing program website into a pdf file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To generate the pdf, follow the steps list below.

### Prerequisites

This the following software is required for this project.

1. python3

2. chrome / chromium browser with dependencies installed

### Installation

1. Install Chrome

    ```
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb
    ```

2. Clone the repo

   ```sh
   git clone https://github.com/klementng/composing-programs-pdf.git
   ```

3. Install python packages

   ```sh
   pip install -r requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Simply run the following commands to generate the PDF file:

```
python main.py
```

## Customization

To modify the output pdf, you can edit the following files:

- urls.py: Include / exclude links

- html_processing: add more html post processing (to remove more section / etc.)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
