# rpSelenzyme

Tool that takes for input a tar.xz with a collection of rpSBML or single rpSBML, scans for the reaction rules and makes a REST request to [Selenzyme](Selenzyme.synbiochem.co.uk) and finds the enzymatic sequences (through Uniprot ID's) of all the reactions in heterologous pathways of rpSBML files.

## Information Flow

### Input

Required information:
* **Unput rpSBML**: Either a single rpSBML or collection pacakged in a tar.xz

Advanced options:
* **Name of the heterologous pathway**: (default: rp_pathway) Groups ID of the heterologous pathway
* **IP address of the rpSelenzyme REST service**: IP address of the REST service

### Output

* **rpSelenzyme**: Either single rpSBML or collection of rpSBML's in a tar.xz

## Installing 

To compile the docker run the following command:

```
docker build -t brsynth/rpselenzyme-standalone:dev .
```

And then run the container (use tmux or -deamon):

```
docker run -p 5000:5000 -e LD_LIBRARY_PATH='/opt/conda/bin/../lib' brsynth/selenzyme-rest:dev
```

### Prerequisites

* Docker - [Install](https://docs.docker.com/v17.09/engine/installation/)
* RDKit - [Install](https://www.rdkit.org/)
* Flask - [Install](https://flask-restful.readthedocs.io/en/latest/)

## Contributing

TODO


## Testing

To test the execution of the tool, untar the test.tar.xz and execute the following command:

```
python run.py -input test/test_rpThermo.tar -input_format tar -taxonomy_format string -taxonomy_input 83333 -output test/test_rpSelenzyme.tar
```

## Versioning

Version 0.1

## Authors

* **Melchior du Lac** 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thomas Duigou
* Joan Hérisson

### How to cite rpSelenzyme?

Carbonell, Pablo, et al. "Selenzyme: Enzyme selection tool for pathway design." Bioinformatics 34.12 (2018): 2153-2154.
