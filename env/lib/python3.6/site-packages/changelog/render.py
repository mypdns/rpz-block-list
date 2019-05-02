#! coding: utf-8
from docutils import nodes

import itertools
import collections


def render_changelog(changelog_directive):
    changes = changelog_directive.get_changes_list(
        changelog_directive.env, changelog_directive.version).values()
    output = []

    id_prefix = "change-%s" % (changelog_directive.version, )
    topsection = _run_top(changelog_directive, id_prefix)
    output.append(topsection)

    bysection, all_sections = _organize_by_section(
        changelog_directive, changes)

    counter = itertools.count()

    sections_to_render = [
        s for s in changelog_directive.sections if s in all_sections]
    if not sections_to_render:
        for cat in changelog_directive.inner_tag_sort:
            append_sec = _append_node(changelog_directive)

            for rec in bysection[(changelog_directive.default_section, cat)]:
                rec["id"] = "%s-%s" % (id_prefix, next(counter))

                _render_rec(changelog_directive, rec, None, cat, append_sec)

            if append_sec.children:
                topsection.append(append_sec)
    else:
        for section in sections_to_render + [
                changelog_directive.default_section]:
            sec = nodes.section(
                '',
                nodes.title(section, section),
                ids=["%s-%s" % (id_prefix, section.replace(" ", "-"))]
            )

            append_sec = _append_node(changelog_directive)
            sec.append(append_sec)

            for cat in changelog_directive.inner_tag_sort:
                for rec in bysection[(section, cat)]:
                    rec["id"] = "%s-%s" % (id_prefix, next(counter))
                    _render_rec(
                        changelog_directive,
                        rec, section, cat, append_sec)

            if append_sec.children:
                topsection.append(sec)

    return output


def _organize_by_section(changelog_directive, changes):
    compound_sections = [
        (s, s.split(" ")) for s in changelog_directive.sections if " " in s]

    bysection = collections.defaultdict(list)
    all_sections = set()
    for rec in changes:
        assert changelog_directive.version == rec['render_for_version']

        inner_tag = rec['tags'].intersection(
            changelog_directive.inner_tag_sort)
        if inner_tag:
            inner_tag = inner_tag.pop()
        else:
            inner_tag = ""

        for compound, comp_words in compound_sections:
            if rec['tags'].issuperset(comp_words):
                bysection[(compound, inner_tag)].append(rec)
                all_sections.add(compound)
                break
        else:
            intersect = rec['tags'].intersection(changelog_directive.sections)
            if intersect:
                for sec in rec['sorted_tags']:
                    if sec in intersect:
                        bysection[(sec, inner_tag)].append(rec)
                        all_sections.add(sec)
                        break
            else:
                bysection[
                    (changelog_directive.default_section, inner_tag)
                ].append(rec)
    return bysection, all_sections


def _append_node(changelog_directive):
    return nodes.bullet_list()


def _run_top(changelog_directive, id_prefix):
    version = changelog_directive._parsed_content.get('version', '')
    topsection = nodes.section(
        '',
        nodes.title(version, version),
        ids=[id_prefix]
    )

    if changelog_directive._parsed_content.get("released"):
        topsection.append(
            nodes.Text("Released: %s" %
                       changelog_directive._parsed_content['released'])
        )
    else:
        topsection.append(nodes.Text("no release date"))

    intro_para = nodes.paragraph('', '')
    len_ = -1
    for len_, text in enumerate(changelog_directive._parsed_content['text']):
        if ".. change::" in text:
            break

    # if encountered any text elements that didn't start with
    # ".. change::", those become the intro
    if len_ > 0:
        changelog_directive.state.nested_parse(
            changelog_directive._parsed_content['text'][0:len_], 0,
            intro_para)
        topsection.append(intro_para)

    return topsection


def _render_rec(changelog_directive, rec, section, cat, append_sec):
    para = rec['node'].deepcopy()

    targetid = "change-%s" % (
        rec['version_to_hash'][changelog_directive.version],
    )
    targetnode = nodes.target('', '', ids=[targetid])
    para.insert(0, targetnode)
    permalink = nodes.reference(
        '', '',
        nodes.Text(u"¶", u"¶"),
        refid=targetid,
        classes=['changeset-link', 'headerlink'],
    )
    para.append(permalink)

    if len(rec['versions']) > 1:

        backported_changes = rec['sorted_versions'][
            rec['sorted_versions'].index(changelog_directive.version) + 1:]
        if backported_changes:
            backported = nodes.paragraph('')
            backported.append(nodes.Text("This change is also ", ""))
            backported.append(nodes.strong("", "backported"))
            backported.append(
                nodes.Text(" to: %s" % ", ".join(backported_changes), ""))
            para.append(backported)

    insert_ticket = nodes.paragraph('')
    para.append(insert_ticket)

    i = 0
    for collection, render, prefix in (
            (rec['tickets'],
             changelog_directive.env.config.changelog_render_ticket, "#%s"),
            (rec['pullreq'],
             changelog_directive.env.config.changelog_render_pullreq,
             "pull request %s"),
            (rec['changeset'],
             changelog_directive.env.config.changelog_render_changeset, "r%s"),
    ):
        for refname in collection:
            if i > 0:
                insert_ticket.append(nodes.Text(", ", ", "))
            else:
                insert_ticket.append(nodes.Text("References: """))
            i += 1
            if render is not None:
                if isinstance(render, dict):
                    if ":" in refname:
                        typ, refval = refname.split(":")
                    else:
                        typ = "default"
                        refval = refname
                    refuri = render[typ] % refval
                else:
                    refuri = render % refname
                node = nodes.reference(
                    '', '',
                    nodes.Text(prefix % refname, prefix % refname),
                    refuri=refuri
                )
            else:
                node = nodes.Text(prefix % refname, prefix % refname)
            insert_ticket.append(node)

    if rec['tags'] and changelog_directive.env.config.changelog_render_tags:
        tag_node = nodes.strong(
            '',
            " ".join(
                "[%s]" % t for t in
                [t1 for t1 in [section, cat] if t1 in rec['tags']] +
                list(sorted(rec['tags'].difference([section, cat])))
            ) + " "
        )
        para.children[0].insert(0, tag_node)

    append_sec.append(
        nodes.list_item(
            '',
            nodes.target('', '', ids=[rec['id']]),
            para
        )
    )


