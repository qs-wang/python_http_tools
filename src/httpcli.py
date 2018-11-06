import click
import os
from os.path import expanduser
import requests
from config import parse_config, create_config, get_config_dict
import json
import logging
import cuid

# set up logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format="[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s()]-12s %(levelname)-8s %(message)s))",
                    datefmt="%m-%d %H:%M")

logger = logging.getLogger('my-http-cli')

CONFIG_DIR = ".flam"
CONFIG_FILE = "config.ini"
HOME = expanduser("~")

CONFIG_FOLDER = HOME + "/" + CONFIG_DIR
CONFIG_PATH = CONFIG_FOLDER + "/" + CONFIG_FILE


@click.group()
def cli():
    pass


@click.command()
@click.argument("key")
@click.argument("value", default="")
@click.option("--profile", "-p", default="DEFAULT", help="The profile name")
def config(key, value, profile):
    if value == "":
        config_dict = load_config_dict_for_profile(profile)
        click.echo("{} = {} for profile: {}".format(
            key, config_dict[key], profile))
    else:
        config = parse_config(CONFIG_PATH)
        if not config.has_section(profile) and profile != "DEFAULT":
            config.add_section(profile)
        config.set(profile, key, value)
        with open(CONFIG_PATH, "wb") as config_file:
            config.write(config_file)


@click.command()
@click.argument("user", default="")
@click.option("--profile", "-p", default="DEFAULT", help="The profile name")
def login(user, profile):
    logger.debug("The profile is {}".format(profile))
    user_name = user
    config = parse_config(CONFIG_PATH)
    config_dict = get_config_dict(config, profile)

    if user_name == "":
        if "user_name" in config_dict:
            user_name = config_dict["user_name"]

    if user_name == "":
        click.prompt("User name", type=str)
    password = click.prompt("Password", hide_input=True)

    if "auth_url" in config_dict:
        auth_url = config_dict["auth_url"]

        headers = {
            "X-Correlation-Id": cuid.cuid()
        }

        logger.debug("Auth url is {}".format( auth_url))

        result = requests.post(
            auth_url , data={"username": user_name, "password": password}, verify=False, headers=headers)

        if result.status_code != 200:
            logger.debug("Login failed with result:{}".format(result))
            click.echo("Login failed")
        else:
            result_dict = json.loads(result.text)
            token = result_dict.get('token', '')

            config.set(profile, 'user_name', user_name)
            config.set(profile, 'token', token)
            with open(CONFIG_PATH, "wb") as config_file:
                config.write(config_file)

            click.echo("Login was successful, token saved")
    else:
        click.echo("Auth url hasn't been configured")


@click.command()
@click.argument("location", default="")
@click.argument("file_name", default="")
@click.option("--profile", "-p", default="DEFAULT", help="The profile name")
def gt(location, file_name, profile):
    config_dict = load_config_dict_for_profile(profile)
    if "token" not in config_dict:
        click.echo("Please login first")
        return

    if "root_url" in config_dict:
        root_url = config_dict["root_url"]
        end_point = root_url + "/" + location
        headers = {
            'authorization': 'Bearer ' + config_dict["token"],
            'X-Correlation-Id': cuid.cuid()
        }

        logger.debug("Endpoint url is {}".format( end_point))

        result = requests.get(end_point, headers=headers, verify=False)

        if result.status_code != 200:
            logger.debug("Get failed with result:{}".format(result))
            click.echo("Rqeust failed")
        else:
            if file_name == '':
                print(json.dumps(result.json()))
            else:
                with open(file_name, 'w') as outfile:
                    json.dump(json.loads(result.text), outfile)
    else:
        click.echo("Root url hasn't been configured")


@click.command()
@click.argument("location", default="")
@click.argument("file_name", default="data.json")
@click.option("--profile", "-p", default="DEFAULT", help="The profile name")
def pt(location, file_name, profile):
    config_dict = load_config_dict_for_profile(profile)
    if "token" not in config_dict:
        click.echo("Please login at first")
        return

    if "root_url" in config_dict:
        root_url = config_dict["root_url"]
        end_point = root_url + "/" + location
        headers = {
            'authorization': 'Bearer ' + config_dict["token"],
            'X-Correlation-Id': cuid.cuid()
        }

        logger.debug("Endpoint url is {}".format( end_point))

        if file_name == 'data.json':
            data_file = os.path.abspath(
                os.path.dirname(__file__)) + '/data.json'
            print(data_file)
        else:
            data_file = file_name

        with open(data_file) as f:
            result = requests.post(
                end_point, headers=headers, verify=False, data=f.read())

            if result.status_code != 200:
                logger.debug("Post failed with result:{}".format(result))
                click.echo("Rqeust failed with status_code:{}".format(
                    result.status_code))
            else:
                click.echo(result.content)
                click.echo("Rqeust sucessful with status_code:{}".format(
                    result.status_code))
    else:
        click.echo("Root url hasn't been configured")


def load_config_dict_for_profile(profile):
    config = parse_config(CONFIG_PATH)
    config_dict = get_config_dict(config, profile)
    return config_dict


cli.add_command(config)
cli.add_command(login)
cli.add_command(gt)
cli.add_command(pt)

if __name__ == "__main__":
    if not os.path.exists(CONFIG_PATH):
        create_config(CONFIG_PATH)
    cli()
