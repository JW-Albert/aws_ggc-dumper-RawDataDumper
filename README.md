# Raw Data Dumper for AWS Greengrass

This project is an AWS Greengrass component that collects and dumps raw data from IoT devices into CSV files. It monitors GPIO states and raw data streams, saving the data when specific conditions are met.

## Features

- Monitors device shadow for GPIO state changes
- Subscribes to raw data topics
- Saves data to CSV files based on GPIO state rules
- Configurable logging levels
- Automatic directory creation for data storage

## Prerequisites

- AWS Greengrass Core v2
- Python 3.7+
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The component requires the following parameters:

- `--thing-name`: Greengrass Thing name
- `--shadow-name`: Greengrass shadow name
- `--rawdata-topic`: Topic to read raw data
- `--write-rule`: Rule to write data
- `--save-directory`: Directory to save CSV files (default: /mnt/rawdata)
- `--log-level`: Log level (default: INFO)

## Usage

Run the component with required parameters:

```bash
python src/main.py --thing-name YOUR_THING_NAME --shadow-name YOUR_SHADOW_NAME --rawdata-topic YOUR_TOPIC --write-rule YOUR_RULE
```

## Data Format

The component saves data in CSV format with the following structure:

1. Metadata header and row containing:
   - timestamp
   - sample_rate
   - data_len
   - data_header
2. Data rows containing the actual measurements

## License

Copyright (c) 2024 Raw Data Dumper Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software for non-commercial purposes only, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

2. The Software may not be used for commercial purposes without explicit written
   permission from the copyright holders.

3. The Software is provided "as is", without warranty of any kind, express or
   implied, including but not limited to the warranties of merchantability,
   fitness for a particular purpose and noninfringement.

4. In no event shall the authors or copyright holders be liable for any claim,
   damages or other liability, whether in an action of contract, tort or otherwise,
   arising from, out of or in connection with the Software or the use or other
   dealings in the Software.
