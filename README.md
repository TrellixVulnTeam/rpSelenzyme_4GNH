# Galaxy rpSelenzyme

Galaxy tool that takes for input a tar.xz with a collection of SBML that scans for the reaction rules, makes a REST request to a selenzyme database and adds the results to the IBISBA annotations of rpSBML's. 

NOTE: temporarely I added selenzyme inside the rpSelenzyme docker image (sort of stupid since we are performing a localhost REST request to a FLASK service running in the same place). Ideally we would like to have another docker with selenzyme running inn the backgroud

## Getting Started

This is a docker galaxy tools, and thus, the docker needs to be built locally where Galaxy is installed. 

### Build the tool

```
docker build --no-cache -t sbc/selenzy .
```

And then run the container (use tmux or -deamon):

```
docker run --network host -p 5000:5000 -e LD_LIBRARY_PATH='/opt/conda/bin/../lib' sbc/selenzy
```

### Prerequisites

TODO

### Installing galaxy tool

Create a new section in the Galaxy tool_cong.xml from the config file:

```
<section id="retro" name="Retro Nodes">
  <tool file="/local/path/config_rpSelenzyme.xml" />
</section>
```

Make sure that docker can be run in root:

```
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart
```

Build the docker image:

```
docker build -t ibisba/rpselenzyme .
```

Make sure that the following job_conf.xml looks like this:

NOTE: we use the host network configuration to use the localhost as a means of calling the service. TODO: ask Joan if there is a better way to communicate between the two dockers.

```
<?xml version="1.0"?>
<job_conf>
  <plugins>
    <plugin id="local" type="runner" load="galaxy.jobs.runners.local:LocalJobRunner" workers="4"/>
  </plugins>
  <destinations default="docker_local_readonly">
    <destination id="local" runner="local" />
    <destination id="docker_local" runner="local">
      <param id="docker_enabled">true</param>
      <param id="docker_sudo">false</param>
      <param id="docker_auto_rm">true</param>
      <param id="docker_set_user">root</param>
      <param id="docker_run_extra_arguments">-net host --mount source=rpcache,destination=/home/rpInspect/cache,readonly --mount source=component_contribution_data,destination=/home/rpInspect/component_contribution/data,readonly</param>
    </destination>
  </destinations>
</job_conf>
```

It is important to run the docker as root user since we will be calling a script that writes files to a temporary folder inside the docker before sending bask to Galaxy

## Running the tests

TODO

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Galaxy](https://galaxyproject.org) - The Galaxy project

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

TODO

## Authors

* **Melchior du Lac** 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thomas Duigou
* Joan Hérisson
