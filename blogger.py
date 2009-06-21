import atom
from docutils.examples import html_parts
import gdata
import gdata.service
import getpass

def login(username, password):
    service = gdata.service.GDataService(username, password)
    service.service = 'blogger'
    service.server = 'www.blogger.com'
    service.ProgrammaticLogin()
    return service

def create_entry(title, content, draft=False):
    entry = gdata.GDataEntry()
    entry.title = atom.Title(title_type='text', text=title)
    entry.content = atom.Content(content_type='html', text=content.encode('utf8'))
    if draft:
        control = atom.Control()
        control.draft = atom.Draft(text='yes')
        entry.control = control
    return entry

def listblogs(service):
    feed = service.Get('/feeds/default/blogs')
    for blog in feed.entry:
        print "%s: %s" % (blog.GetSelfLink().href.split('/')[-1],
            blog.title.text)

def listposts(service, blogid):
    feed = service.Get('/feeds/' + blogid + '/posts/default')
    for post in feed.entry:
        print post.GetEditLink().href.split('/')[-1], post.title.text, "[DRAFT]" if is_draft(post) else ""

def is_draft(post):
    return post.control and post.control.draft and post.control.draft.text == 'yes'

def read_blogpost(filename, rawhtml, rawhtmltitle):
    if not rawhtml:
        parts = html_parts(open(filename, 'rb').read().decode('utf8'))
        title = parts['title']
        content = parts['body']
    else:
        title = opts.title
        content = open(filename, 'rb').read().decode('utf8')
    return title, content

def parse_command_line():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--username")
    parser.add_option("--password")
    parser.add_option("--blogid")
    parser.add_option("--rawhtml", action="store_true", default=False)
    parser.add_option("--title", help="Only used with --rawhtml")
    parser.add_option("--listblogs", action="store_true", default=False)
    parser.add_option("--listposts", action="store_true", default=False)

    opts, args = parser.parse_args()
    if not opts.username:
        opts.username = raw_input("Username: ")
    if not opts.password:
        opts.password = getpass.getpass()
    return opts, args

if __name__ == '__main__':
    opts, args = parse_command_line()

    if opts.listblogs:
        listblogs(login(opts.username, opts.password))
    elif opts.listposts:
        listposts(login(opts.username, opts.password), opts.blogid)
    else:
        if not args: parser.error("Specify file name")

        title, content = read_blogpost(args[0], opts.rawhtml, opts.title)
        login(opts.username, opts.password).Post(
            create_entry(title, content),
            '/feeds/' + opts.blogid + '/posts/default')