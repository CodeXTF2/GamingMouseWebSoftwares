# Gaming peripheral web software archive

This repository serves to archive fully offline usable (albeit maybe not as pretty sometimes) copies of gaming peripheral web softwares.
  
This is mainly for the following reasons:
- in case one day the vendor shuts down the webapp (or just closes shop entirely)
- in case anyone wants to use a past version of the web software
- possible modifications/upgrades (if anyone wants to)

Also, self hosted web software is a lot more transparent code wise than installable apps, due to less reverse engineering needed to audit for malware, and *generally* safer, for anyone concerned about downloading .exe files from a chinese vendor. 

folder name is just the default filename produced by the following command:
```
wget2 --mirror --convert-links --adjust-extension --page-requisites --no-parent --max-threads=32 example.com
```

I will be updating this with any web software I own the peripheral for (and can test to be working). Feel free to submit PRs with additional brands softwares.   
**PLEASE TEST THAT THE COPY WORKS LOCALLY, WITH THE HARDWARE, BEFORE SUBMITTING A PR**

to test, simply enter the folder and run:
```
python -m http.server 5000
```

and open the url in your browser:
```
http://localhost:5000
```

and test features of the webapp.  

If it mostly works, but has some quirks (or broken features) please create a README.md in the folder and note them down.

## Translating
I have made a simple translator in the translator folder. To run it, run the translate_local.py script to create a translations.json file, then run the apply_translations.py script.

You will need to install the argostranslate package from pip.

## Disclaimer
All these softwares are owned by their respective brands/vendors. This repository is just an archive of publicly available copies of their code/software
