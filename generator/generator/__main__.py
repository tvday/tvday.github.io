"""Build static HTML site from directory of HTML templates and plain files."""
import ruamel.yaml as yaml

import sys
import pathlib
import shutil
import jinja2
import click


def render(output_dir, template_env, configs, verbose):
    """Render the htmls using the templates and configurations."""
    for config in configs:
        template_file = config['template']
        url = config['url'].lstrip("/")
        if not (output_dir / url).exists():
            (output_dir / url).mkdir(parents=True)
        output_path = output_dir / url / 'index.html'

        try:
            template = template_env.get_template(template_file)
        except jinja2.TemplateError:
            print('ERROR: error in retrieving template %s' % template_file)
            sys.exit(1)

        output_path.write_text(template.render(config['context']))
        if verbose:
            print('Rendered %s -> %s' % (template_file, output_path))


@click.command()
@click.option('-o', '--output', help='Output directory.')
@click.option('-v', '--verbose', help='Print more output.', is_flag=True)
@click.argument('INPUT_DIR')
def main(output, verbose, input_dir):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)
    if not input_dir.is_dir():
        print('ERROR: %s is not a directory' % input_dir)
        sys.exit(1)
    if not output:
        output_dir = input_dir / 'html'
    else:
        output_dir = pathlib.Path(output)
    if output_dir.exists():
        shutil.rmtree(output_dir)
        # print('ERROR: %s already exists' % output_dir)
        # sys.exit(1)
    output_dir.mkdir(parents=True)

    if (input_dir / 'static').is_dir():
        shutil.copytree(input_dir / 'static', output_dir, dirs_exist_ok=True)
        if verbose:
            print('Copied %s -> %s' % ((input_dir / 'static'), output_dir))

    template_dir = input_dir / 'templates'
    if not template_dir.is_dir():
        print('ERROR: %s not found' % template_dir)
        sys.exit(1)

    try:
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )
    except jinja2.TemplateError:
        print('ERROR: error in creating template environment from %s'
              % template_dir)

    try:
        configs = yaml.safe_load(open(input_dir / 'config.yaml'))
    except yaml.YAMLError:
        print('ERROR: error in reading %s' % (input_dir / 'config.yaml'))
        sys.exit(1)
    except FileNotFoundError:
        print('ERROR: %s not found' % (input_dir / 'config.json'))
        sys.exit(1)

    render(output_dir, template_env, configs, verbose)


if __name__ == "__main__":
    main()
