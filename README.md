# Advanced-Public-Transportation-System-Software-Implementation

This repository contains the code for scalable implementation of the advanced urban public transportation system for the scenarios of developing countries where the Intelligent Transportation System (ITS) infrastructure deployment is limited. 

## Documentation:
Please refer the following [link](https://pruthvishrajput.github.io/Advanced-Public-Transportation-System-Software-Implementation/) for the documentation of the proposed system.

## Dataset: 
The project dataset can be found in the given [link](https://drive.google.com/drive/folders/1ysoAymbBmF03MFmwlD9ul9z-ISxZDWU_?usp=sharing).

## Reproducible capsule (For execution in a single click)


This repository contains the code for scalable implementation of the advanced urban public transportation system for the scenarios of developing countries where the Intelligent Transportation System (ITS) infrastructure deployment is limited. The software achieves scalability by executing the minimal task in real-time and remaining computation in an offline mode. 

## Execution of software
### Reproducible capsule
The reproducible capsule contains all the codes, dataset, and computation environment dependencies (or libraries) in a docker. It guarantees the reproducibility of the code. 

Click [here](https://codeocean.com/capsule/9953786/tree) to execute the reproducible capsule.

### Downloading the file on the local system.
The user can download/clone the source code repository in the local system to execute the APTS solution in their system. The user must download the following software (and libraries) before running the code.

#### List of required software (and libraries) for local system execution
1. Python3
2. MongoDB community server
3. Python libraries: astropy ≥ 5.1, folium ≥ 0.12.1.post1, ipywidgets ≥ 8.0.2, matplotlib ≥ 3.6.0, notebook ≥ 6.4.12, numpy ≥ 1.23.3, openpyxl ≥ 3.0.10, pandas ≥ 1.5.0, pymongo ≥ 4.2.0 (and xfs file system), scikit-learn ≥ 1.1.2, scipy ≥ 1.9.1, sklearn≥ 0.0
  - To install prerequisite, execute the commands mentioned in `Command.txt`   

#### Local implementation
- Compatibility & Requirements
  - Tested & Preferred: Ubuntu 24.04 LTS (fully verified)
  - Also Supported: Windows 10 / 11 (via Native Command Prompt/PowerShell or WSL)

### Executing your own data records 

- The users can execute the APTS solutions using the project dataset. 
- Alternatively,  the users can use their own compatible datasets by placing them in the appropriate subfolder of `UserData` folder and selecting the variable `ProjectDataUsed` value as `False`. 
- The `UserData` folder can contain the empty folders `LocationRecords`, `TransportMode`, and `SitStandRecord` folders where the users can place their trip data with the above-mentioned record and file name format. 


# License
MIT License

Copyright (c) 2022 Pruthvish Rajput, Manish Chaturvedi, and Vivek Patel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
