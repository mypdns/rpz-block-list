import collections
import copy
import hashlib as md5
import os
import re
import warnings

from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util.console import bold
from sphinx.util.osutil import copyfile
from sphinx.util import status_iterator
from sphinx.util import logging
from . import render

LOG = logging.getLogger(__name__)


def _is_html(app):
    return app.builder.name in ('html', 'readthedocs')


def _comma_list(text):
    return re.split(r"\s*,\s*", text.strip())


def _parse_content(content):
    d = {}
    d['text'] = []
    idx = 0
    for line in content:
        idx += 1
        m = re.match(r' *\:(.+?)\:(?: +(.+))?', line)
        if m:
            attrname, value = m.group(1, 2)
            d[attrname] = value or ''
        elif idx == 1 and line:
            # accomodate a unique value on the edge of .. change::
            continue
        else:
            break
    d["text"] = content[idx:]
    return d


class EnvDirective(object):
    @property
    def env(self):
        return self.state.document.settings.env

    @classmethod
    def get_changes_list(cls, env, hash_on_version):
        key = ('ChangeLogDirective_changes', hash_on_version)
        if key not in env.temp_data:
            env.temp_data[key] = collections.OrderedDict()
        return env.temp_data[key]


class ChangeLogDirective(EnvDirective, Directive):
    """Implement the ``.. changelog::`` directive.

    """
    has_content = True

    default_section = 'misc'

    def run(self):
        self._parse()

        if not ChangeLogImportDirective.in_include_directive(self.env):
            return render.render_changelog(self)
        else:
            return []

    def _parse(self):
        # 1. pull in global configuration from conf.py
        self.sections = self.env.config.changelog_sections
        self.inner_tag_sort = self.env.config.changelog_inner_tag_sort + [""]

        # 2. examine top level directives inside the .. changelog::
        # directive.  version, release date
        self._parsed_content = parsed = _parse_content(self.content)
        self.version = version = parsed.get('version', '')
        self.release_date = parsed.get('released', None)
        self.is_released = bool(self.release_date)
        self.env.temp_data['ChangeLogDirective'] = self

        content = self.content

        # 3. read extra per-file included notes
        if 'include_notes_from' in parsed:
            if content.items and content.items[0]:
                source = content.items[0][0]
                path = os.path.join(
                    os.path.dirname(source), parsed['include_notes_from'])
            else:
                path = parsed['include_notes_from']
            if not os.path.exists(path):
                raise Exception("included nodes path %s does not exist" % path)

            content = copy.deepcopy(content)

            files = [
                fname for fname in os.listdir(path) if fname.endswith(".rst")
            ]
            for fname in status_iterator(
                files,
                "reading changelog note files (version %s)..." % version,
                "purple", length=len(files), verbosity=self.env.app.verbosity
            ):
                fpath = os.path.join(path, fname)
                with open(fpath) as handle:
                    content.append("", path, 0)
                    for num, line in enumerate(handle):

                        if "\t" in line:
                            warnings.warn(
                                "file %s has a tab in it! please "
                                "convert to spaces." % fname)
                            line = line.replace("\t", "    ")
                        line = line.rstrip()
                        content.append(
                            line, path, num
                        )

        # 4. parse the content of the .. changelog:: directive. This
        # is where we parse individual .. change:: directives and construct
        # a list of items, stored in the env via self.get_changes_list(env)
        p = nodes.paragraph('', '',)
        self.state.nested_parse(content[1:], 0, p)


class ChangeLogImportDirective(EnvDirective, Directive):
    """Implement the ``.. changelog_imports::`` directive.

    Here, we typically load in other changelog.rst files which may feature
    elements that also apply to our current changelog.rst file, when they
    specify the ``:version:`` modifier.

    """
    has_content = True

    @classmethod
    def in_include_directive(cls, env):
        return 'ChangeLogDirective_includes' in env.temp_data

    def run(self):
        # tell ChangeLogDirective we're here, also prevent
        # nested .. include calls
        if not self.in_include_directive(self.env):
            self.env.temp_data['ChangeLogDirective_includes'] = True
            p = nodes.paragraph('', '',)
            self.state.nested_parse(self.content, 0, p)
            del self.env.temp_data['ChangeLogDirective_includes']

        return []


class ChangeDirective(EnvDirective, Directive):
    """Implement the ``.. change::`` directive.

    """
    has_content = True

    def run(self):
        # don't do anything if we're not inside of a version
        if 'ChangeLogDirective' not in self.env.temp_data:
            return []

        content = _parse_content(self.content)
        body_paragraph = nodes.paragraph('', '',)
        sorted_tags = _comma_list(content.get('tags', ''))
        changelog_directive = self.env.temp_data['ChangeLogDirective']
        declared_version = changelog_directive.version
        versions = set(
            _comma_list(content.get("versions", ""))).difference(['']).\
            union([declared_version])

        # if we don't refer to any other versions and we're in an include,
        # skip
        if len(versions) == 1 and \
                ChangeLogImportDirective.in_include_directive(self.env):

            return []

        self.state.nested_parse(content['text'], 0, body_paragraph)

        raw_text = _text_rawsource_from_node(body_paragraph)
        tickets = set(_comma_list(content.get('tickets', ''))).difference([''])
        pullreq = set(_comma_list(content.get('pullreq', ''))).difference([''])
        tags = set(sorted_tags).difference([''])

        for hash_on_version in versions:
            issue_hash = _get_robust_version_hash(
                raw_text, hash_on_version, tickets, tags)

            rec = ChangeLogDirective.get_changes_list(
                changelog_directive.env, hash_on_version).setdefault(
                issue_hash, {})
            if not rec:
                rec.update({
                    'hash': issue_hash,
                    "render_for_version": hash_on_version,
                    'tags': tags,
                    'tickets': tickets,
                    'pullreq': pullreq,
                    'changeset': set(
                        _comma_list(content.get('changeset', ''))
                    ).difference(['']),
                    'node': body_paragraph,
                    'raw_text': raw_text,
                    'type': "change",
                    "title": content.get("title", None),
                    'sorted_tags': sorted_tags,
                    "versions": versions,
                    "version_to_hash": {
                        version: _get_legacy_version_hash(raw_text, version)
                        for version in versions
                    },
                    "source_versions": [declared_version],
                    "sorted_versions": list(
                        reversed(sorted(versions, key=_str_version_as_tuple)))
                })
            else:
                LOG.info(
                    "Merging changelog record '%s' from version(s) %s "
                    "with that of version %s",
                    _quick_rec_str(rec),
                    ", ".join(rec['source_versions']),
                    declared_version
                )
                rec["source_versions"].append(declared_version)

                assert rec['raw_text'] == raw_text
                assert rec['tags'] == tags
                assert rec["render_for_version"] == hash_on_version

                rec['tickets'].update(tickets)
                rec['pullreq'].update(pullreq)
                rec['changeset'].update(
                    set(
                        _comma_list(content.get('changeset', ''))).
                    difference([''])
                )
                rec['versions'].update(versions)

                rec['version_to_hash'].update(
                    {
                        version: _get_legacy_version_hash(raw_text, version)
                        for version in versions
                    }
                )
                rec["sorted_versions"] = list(
                    reversed(
                        sorted(rec['versions'], key=_str_version_as_tuple)))

        return []


def _quick_rec_str(rec):
    """try to print an identifiable description of a record"""

    if rec['tickets']:
        return "[tickets: %s]" % ", ".join(rec["tickets"])
    else:
        return "%s..." % rec["raw_text"][0:25]


def _get_legacy_version_hash(raw_text, version):
    # this needs to stay like this for link compatibility
    # with thousands of already-published changelogs
    to_hash = "%s %s" % (version, raw_text[0:100])
    return md5.md5(to_hash.encode('ascii', 'ignore')).hexdigest()


def _get_robust_version_hash(raw_text, version, tickets, tags):
    # this needs to stay like this for link compatibility
    # with thousands of already-published changelogs
    to_hash = "%s %s %s %s" % (
        version, ", ".join(tickets), ", ".join(tags), raw_text)
    return md5.md5(to_hash.encode('ascii', 'ignore')).hexdigest()


def _text_rawsource_from_node(node):
    src = []
    stack = [node]
    while stack:
        n = stack.pop(0)
        if isinstance(n, nodes.Text):
            src.append(n.rawsource)
        stack.extend(n.children)
    return "".join(src)


_VERSION_IDS = {}


def _str_version_as_tuple(ver):
    if ver in _VERSION_IDS:
        return _VERSION_IDS[ver]

    out = []
    for dig in ver.split("."):
        try:
            out.append(int(dig))
        except ValueError:
            out.append(dig)
    _VERSION_IDS[ver] = result = tuple(out)
    return result


def make_ticket_link(
        name, rawtext, text, lineno, inliner,
        options={}, content=[]):
    env = inliner.document.settings.env
    render_ticket = env.config.changelog_render_ticket or "%s"
    prefix = "#%s"
    if render_ticket:
        ref = render_ticket % text
        node = nodes.reference(rawtext, prefix % text, refuri=ref, **options)
    else:
        node = nodes.Text(prefix % text, prefix % text)
    return [node], []


def add_stylesheet(app):
    app.add_stylesheet('changelog.css')


def copy_stylesheet(app, exception):
    app.info(
        bold('The name of the builder is: %s' % app.builder.name), nonl=True)

    if not _is_html(app) or exception:
        return
    app.info(bold('Copying sphinx_paramlinks stylesheet... '), nonl=True)

    source = os.path.abspath(os.path.dirname(__file__))

    # the '_static' directory name is hardcoded in
    # sphinx.builders.html.StandaloneHTMLBuilder.copy_static_files.
    # would be nice if Sphinx could improve the API here so that we just
    # give it the path to a .css file and it does the right thing.
    dest = os.path.join(app.builder.outdir, '_static', 'changelog.css')
    copyfile(os.path.join(source, "changelog.css"), dest)
    app.info('done')


def setup(app):
    app.add_directive('changelog', ChangeLogDirective)
    app.add_directive('change', ChangeDirective)
    app.add_directive('changelog_imports', ChangeLogImportDirective)
    app.add_config_value("changelog_sections", [], 'env')
    app.add_config_value("changelog_inner_tag_sort", [], 'env')
    app.add_config_value("changelog_render_ticket", None, 'env')
    app.add_config_value("changelog_render_pullreq", None, 'env')
    app.add_config_value("changelog_render_changeset", None, 'env')
    app.add_config_value("changelog_render_tags", None, 'env')
    app.connect('builder-inited', add_stylesheet)
    app.connect('build-finished', copy_stylesheet)
    app.add_role('ticket', make_ticket_link)
