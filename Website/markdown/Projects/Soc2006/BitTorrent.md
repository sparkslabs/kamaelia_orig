---
pagename: Projects/Soc2006/BitTorrent
last-modified-date: 2008-09-20
page-template: default
page-type: text/markdown
page-status: current|legacy|needsupdate|deprecated|recommended
---
\

**SoC Project**: BitTorrent 
===========================

This project was implemented by Ryan for Google Summer of Code 2006.
There were however also other applications in this area for SoC 2006.
Ryan\'s description here below will be merged into the mainline projects
description area since the code was merged into the mainline! There were
2 other project applications in this area that are summarised here
(after Ryans). Those descriptions contain the depersonalised content,
which can be consolidated as necessary. The depersonalisation is for
privacy reasons, credit is here due to those who spent the time writing
these descriptions.

Creation of an integrated BitTorrent component for Kamaelia (implemented) 
-------------------------------------------------------------------------

::: {align="right"}
Successfully implemented by Ryan over the course of SoC 2006\
:::

Original Goals 
--------------

Creation of an integrated BitTorrent component for Kamaelia

Kamaelia currently lacks a P2P toolset for content delivery. Adding
BitTorrent client functionality to Kamaelia would allow BitTorrent to
act as an end-point for a component chain. It would act upon control
messages/signals sent to it and Eventually this could lead to the BBC
being able to distribute many terabytes of its archive without incurring
massive bandwidth requisites.

Deliverables
------------

1.  #### New Kamaelia components

    Creation of an Kamaelia component or components able to:

    a.  Be controlled by other Kamaelia components
    b.  Download data using the BitTorrent protocol
    c.  Upload data using the BitTorrent protocol
    d.  Create .torrent files for serving based on messages from other
        components

2.  #### Documentation

\

Given sufficient time the following extra features will also be
implemented:

3.  #### Tracker interaction

    a.  Automatic upload of .torrent files to a webserver for
        distribution
    b.  Automatic download of new .torrent files from a webserver

4.  #### Stream \<-\> Torrent

    a.  Deconstruction of a data stream into separate blocks
    b.  Reconstruction of downloaded blocks a single logical stream

5.  #### UI

    User interface that abstracts the process from users, presenting a
    simple stream/programme selection, reconstructed the stream as the
    earlier parts are played

\

Project Details
---------------

I plan to integrate the Mainline (official) BitTorrent client with
Kamaelia, encapsulating it as a threaded component to prevent it
blocking an entire pipeline and removing the requirement for the client
to yield periodically. This should require few if any changes to the
core BitTorrent code, allowing updates to BitTorrent to be easily
supported by my component. In order to interface with Kamaelia my
current plan is to modify the console bittorrent-console.py user
interface so that rather than outputting to the console it uses
outboxes. Rather than transferring downloaded files via outboxes, they
will be stored as a file on disk that can be read by a separate
component.

I intend to allow pseudo-real-time delivery of streaming data by
splitting it into chunks of a predetermined number of bytes, and
uploading these chunks to the BitTorrent network as they are completed.
Such should allow live video to be distributed to broadband users with a
delay in terms of minutes, without requiring the video feed to come to
an end.

------------------------------------------------------------------------

\

### Project Title: BitTorrent client/seeder component

\
Benefits to Kamaelia: This component could be one of the building blocks
of a new platform independent BBC Internet Media Player, which would let
non-Windows users access this service. In addition to this specific use,
in media content delivery having an efficient distribution system is a
key element. For example, coupled with DRM it could be used to
distribute the stock footage the BBC sells. BitTorrent helps develop a
very scalable method for delivering content to users. Not only this
would save bandwidth costs, but for example if a server-side application
using kamaelia goes for using this component to act as a BitTorrent
server, this protocol being a standard end-users would be free to use
their favorite BitTorrent client application to interact with the server
application. For developer using kamaelia, this would be a very simple
way to let applications make simple use of BitTorrent to download and
upload data.\
\
Synopsis:\
This project aims at developing kamaelia components letting applications
rely on the BitTorrent protocol for content delivery and download. The
component will be broken down into sub-elements that could be used with
different peer to peer protocols than BitTorrent. The objective is to
let programmers very easily integrate BitTorrent support into their
applications.\
\
Deliverables:\
\
\* Will deliver:\
\
The first component would handle file management, to let the application
write downloaded files in the most efficient way. As BitTorrent
downloads chunks of data in random order, this introduces various issues
regarding the efficiency of file access, with possible solutions such as
creating an empty file at the beginning of the download that will be
modified every time a new chunk of data is collected. This component
aims at providing solutions to those issues and provide a file access
manager that could be used for any protocol such as BitTorrent that
could result in random file writes. It is important to note that the
design of the component will be so that it is not only for BitTorrent
and can be used in a more general way.\
\
A connection manager. BitTorrent tends to be using many connections at
once, and this component would help managing how many connections at a
time are open and methods to open/close them. BitTorrent\'s efficiency
is very dependent on how many connections at a time are open. Some
routers react badly to the big amount\
of simultaneous connections BitTorrent uses, and usually BiTorrent
clients lack the ability to adapt to this issue. This component would
aim at dynamically adapting the pool of connections BitTorrent uses to
help it be more efficient. Again this component will be designed so that
it can be used with other protocols relying on many simultaneous
connections.\
\
BitTorrent tools. This component will provide low level BitTorrent
tools, such as bencoding/bdecoding, metainfo management, used by both
BitTorrent peer and tracker applications.\
\
BitTorrent peer component. This is the main objective of the project,
which relies on the three previews low level components. It will let
applications download and upload data using the BitTorrent protocol.\
\
\* Given sufficient time:\
\
A BitTorrent tracking component. Managing peers efficiently and
calculating data regarding the various torrents tracked. This component
will manage statistics and provide easy access to it, leaving the
developer free to use other components for the data display. The peer
management part of the component could lead to separating them into
lower level components.\
\
It is likely the above will be adapted during the research and design
phase of the project. For example it may come out of the design that
mechanisms currently in the BitTorrent peer component could be extracted
into more generalist low level components.\
\
Project Details:\
\
The project is likely to start by studying the official BitTorrent
client source code and make sense of the way it implements the protocol.
There are many elements were a better solution could be searched for,
especially for the choking/unchoking algorithm. Comparing he performance
should be easy once the basics have been developed, it will be a matter
of comparing how fast the same torrent is downloaded using the official
client and the one developed during this project.\
\
I will design on paper the various components included in this project,
so that they integrate well into the kamaelia architecture. It is
important to see how the support of bittorrent can be included while
still keeping the philosophy underlying in kamaelia.\
\
The test phase will be crucial. There are so many elements in the
BitTorrent protocol that could go wrong if some clients don\'t behave as
described in the standard. This phase will probably require developing
\'bad clients\' that would behave in a non-standard way in order to
stress test the BitTorrent client developed for kamaelia. Same goes for
the file manager, test applications will be necessary in order to see
how it behaves in extreme conditions.\
\
Project Schedule:\
\
23rd May -\> 1st June:\
Study of the problem and how it can be solved. Design of the components
architecture on paper. Playing around with kamaelia and its source code
to get a better idea of its philosophy and how it works.\
\
1st June -\> 7th June:\
Development of the file management component. Tests sets and preliminary
design of the stress testing application.\
\
7th June -\> 14th June:\
Testing and debugging of the file management component. By the end of
the period the component should be considered validated and fully
working.\
\
15th June -\> 23th June:\
Development of the connections manager component. Tests sets and
preliminary design of the stress testing application. It would be
interesting to see how it can be tested with simpler protocols than
BitTorrent (such as FTP/HTTP downloads).\
\
24th June -\> 30th June:\
Testing and debugging of the connections manager component. By the end
of the period the component should be considered validated and fully
working.\
\
1st July -\> 10th July:\
Complete development, testing and debugging of the BitTorrent tools
component. This aspect should be more straightforward than the rest of
the project, and should give time to test more the previously developed
component, as well as correcting the design of the peer component.\
\
11th July -\> 25th July:\
Development of the peer component. Tests sets and preliminary design of
the stress testing application. Tests for the previously developed
components should be updated to take into consideration how this one
makes use of the previous ones.\
\
26th July -\> 2nd August:\
Final testing and debugging of all the components developed during the
project.\
\
3rd August -\> 21st August:\
Buffer period, which will either be used to develop the tracker
component or for additional time on the previous tasks if they run
late.\
\
References:\
http://www.bittorrent.org/protocol.html\
http://wiki.theory.org/BitTorrentSpecification\
\

------------------------------------------------------------------------

\

### Project title: Creation of an integrated bittorrent component

\
:Benefits:\
\
Kamaelia and the BBC would benefit from the ability to distribute large
media files quickly and cheaply.\
\
:Building a bittorrent component for the Kamaelia toolkit:\
\
The bittorrent protocol is a very effective way of distributing large
files between many clients. Once a client has acquired a piece of a
file, it can start to upload that piece to other clients. This uploading
between clients has two major advantages: First, the more clients
downloading means more clients uploading so download speeds are higher.
Second, the cost of bandwidth is spread between the clients and not a
few central servers.\
\
These advantages of the bittorrent protocol make it very suitable to
distribute media such as audio and video, the file sizes are large and
often there will be many clients wanting the data at any time.\
\
My proposal is to create a bittorrent component for the Kamaelia project
as described in http://tinyurl.com/oephq. This would be useful for
creating applications that need to acquire a lot of data (such as a
video player) but do not need the data right away.\
\
:Example usage case:\
\
Mike (a hypothetical user) loads up his media player build around
Kamaelia. He has just developed an interest in gardening and so using
the media players built in search he finds a list of series about
gardening. Seeing one he likes the look of, he clicks on a subscribe
button. This subscription is done using RSS or something similar. When a
new episode of his subscribed program becomes available, the following
happens:\
\
1. Mike\'s media player discovers the new episode through the subscribed
RSS feed.\
2. The media player then starts the bittorrent client component in the
background and sends the .torrent file provided in the RSS feed to it.\
3. The bittorrent component starts to download. Because there are many
other people subscribed to the same gardening show there are many people
uploading so the download is nice a quick, perhaps just a few hours.\
4. Once the download is complete, the bittorrent client component send
sends a message to the media player saying the data is ready.\
5. The media player then informs mike that a new episode is ready to
watch, perhaps by placing an entry in a visible playlist.\
6. Mike see\'s the new episode and clicks play.\
\
Most of this process is hidden from Mike. He does not need to know about
RSS feeds or that an episode of a subscribed program is available until
it has been downloaded and is ready to watch.\
\
:Deliverables:\
\
- Bittorrent client component, full bittorrent protocol support,
headless operation.\
- Control component for clients to download and view media.\
- Control component for distributing media, control uploading
(seeding).\
\
:Project details:\

BitTorrent
==========

This project was implemented by Ryan for Google Summer of Code 2006.

\

Original Goals 
--------------

Creation of an integrated BitTorrent component for Kamaelia

Kamaelia currently lacks a P2P toolset for content delivery. Adding
BitTorrent client functionality to Kamaelia would allow BitTorrent to
act as an end-point for a component chain. It would act upon control
messages/signals sent to it and Eventually this could lead to the BBC
being able to distribute many terabytes of its archive without incurring
massive bandwidth requisites.

Deliverables
------------

1.  #### New Kamaelia components

    Creation of an Kamaelia component or components able to:

    a.  Be controlled by other Kamaelia components
    b.  Download data using the BitTorrent protocol
    c.  Upload data using the BitTorrent protocol
    d.  Create .torrent files for serving based on messages from other
        components

2.  #### Documentation

\

Given sufficient time the following extra features will also be
implemented:

3.  #### Tracker interaction

    a.  Automatic upload of .torrent files to a webserver for
        distribution
    b.  Automatic download of new .torrent files from a webserver

4.  #### Stream \<-\> Torrent

    a.  Deconstruction of a data stream into separate blocks
    b.  Reconstruction of downloaded blocks a single logical stream

5.  #### UI

    User interface that abstracts the process from users, presenting a
    simple stream/programme selection, reconstructed the stream as the
    earlier parts are played

\

Project Details
---------------

I plan to integrate the Mainline (official) BitTorrent client with
Kamaelia, encapsulating it as a threaded component to prevent it
blocking an entire pipeline and removing the requirement for the client
to yield periodically. This should require few if any changes to the
core BitTorrent code, allowing updates to BitTorrent to be easily
supported by my component. In order to interface with Kamaelia my
current plan is to modify the console bittorrent-console.py user
interface so that rather than outputting to the console it uses
outboxes. Rather than transferring downloaded files via outboxes, they
will be stored as a file on disk that can be read by a separate
component.

I intend to allow pseudo-real-time delivery of streaming data by
splitting it into chunks of a predetermined number of bytes, and
uploading these chunks to the BitTorrent network as they are completed.
Such should allow live video to be distributed to broadband users with a
delay in terms of minutes, without requiring the video feed to come to
an end.

\
\
I expect the best way to do this will be to create a bittorrent client
component first, which can run in the background and be controlled by
other components though a documented messaging interface. Control
components will have the ability to start/stop a torrent, control
download and upload rates, query progress and serve data to another
Kamaelia component once downloading is complete.\
\
Many other components could then be written which can control the
bittorrent client. Control components could be media players using
pygame as an interface, or components for controlling the seeding
(initial uploading) of a new file.\
\
:Project schedule:\
\
- Become familiar with Kamaelia framework. This should not take too
long, a week or so.\
\
- Research and discuss with other Kamaelia developers the best way to
build the bittorrent client component. This includes deciding on the
messaging protocol between this and other components that will use it.\
\
- Build bittorrent client component. This is the most important
deliverable and has priority. Once complete the rest of the summer can
be spent working on components that use this client component.\
\
- Build component to control seeding/uploading of a new torrent. Used to
distribute new media.\
- Build a component for clients to request and once downloaded, view the
contents of a torrent.\
\
