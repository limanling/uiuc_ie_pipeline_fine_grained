#!/usr/bin/env perl

=head1 NAME

ltfzip2rsd.perl

=head1 LICENSE

ltfzip2rsd.perl is made available under the BSD 2-Clause License,
http://opensource.org/licenses/BSD-2-Clause.

Copyright (c) 2015 Trustees of the University of Pennsylvania

=head1 SYNOPSIS

  ltfzip2rsd.perl [-o output_dir] [path/to/]file.ltf.zip

=head1 DESCRIPTION

Given the name of an existing ltf.zip archive file, this script will
extract each ltf.xml data file from the archive, and re-create the
original "raw source data" (rsd.txt) file from which the ltf.xml was
derived.

By default, each output file will be placed in a directory called
"rsd", in the user's current working directory.

Use the "-o" option to select a different directory path for storing
the output.

In either case, the output directory will be created if necessary; if
it already exists and happens to contain rsd.txt files whose names
match ltf.xml files in the zip archive, those existing rsd.txt files
will be overwritten.

There will always be a 1-line report on stderr, showing the path being
used for output.  Any problems that occur with the input or output
files will also be reported on stderr.

=head1 AUTHOR

David Graff <graff@ldc.upenn.edu>

=cut

use strict;
use File::Spec;
use File::Path qw/make_path/;
use Digest::MD5 qw/md5_hex/;
use Encode qw/decode_utf8 encode_utf8/;
use IO::Uncompress::Unzip  qw/$UnzipError/;

my $Usage = "Usage: $0 [-o output_dir] [path/to/]file.ltf.zip\n";
my ( $inp_zip, $out_path );
if ( @ARGV and -f $ARGV[-1] ) {
    $inp_zip = pop @ARGV;
    $out_path = "rsd";
}
if ( @ARGV == 2 and $ARGV[0] eq '-o' ) {
    shift @ARGV;
    $out_path = shift @ARGV;
}
die $Usage unless ( $inp_zip and @ARGV == 0 );

make_path( $out_path ) unless ( -d $out_path ); # if this call fails, it "croaks", and we die right here.
warn "$0: creating output files under $out_path\n"; # report and continue if make_path succeeds

# the next block of code has been adapted from the IO::Uncompress::Unzip manual page
# (see the section labeled "Walking through a zip file")

my $zip = new IO::Uncompress::Unzip $inp_zip
    or die "Cannot open $inp_zip: $UnzipError\n";

my $status;
for ( $status = 1; ! $zip->eof(); $status = $zip->nextStream())
{
    my $name = $zip->getHeaderInfo()->{Name};
    next unless ( $name =~ /\.ltf.xml\z/ );
    my $xmlstr = '';
    my $buff;
    while (( $status = $zip->read( $buff )) > 0) {
        $xmlstr .= $buff;
    }
    die "ERROR: zip read failure on $name\n" if $status < 0;

    ( my $oname = $name ) =~ s:^ltf/::;
    $oname =~ s/ltf.xml\z/rsd.txt/;

    convert_and_save( decode_utf8( $xmlstr ), $name, "$out_path/$oname" );
}

sub convert_and_save
{
    my ( $xmlstr, $ifile, $opath ) = @_;
    my $last_ofs = 0;
    my $raw_out = '';
    my ( $start_ch, $end_ch, $raw_ch_count, $raw_cksum );
    for ( split( /\n/, $xmlstr )) {
        if ( /<DOC / ) {
            if ( /raw_text_char_length="(\d+)" raw_text_md5="(\w+)"/ ) {
                $raw_ch_count = $1;
                $raw_cksum = $2;
            }
            else {
                warn "ERROR: $ifile skipped: DOC tag malformed\n";
                return
            }
        }
        elsif ( /<SEG .*?start_char="(\d+)" end_char="(\d+)"/ ) {
            ( $start_ch, $end_ch ) = ( $1, $2 );
        }
        elsif ( /<ORIGINAL_TEXT>(.*?)</ ) {
            my $otxt = $1;
            $otxt =~ s/&lt;/</g;
            $otxt =~ s/&gt;/>/g;
            $otxt =~ s/&amp;/&/g;
            if ( $start_ch > $last_ofs ) {
                $raw_out .= "\n" x ( $start_ch - $last_ofs );
            }
            $raw_out .= $otxt . "\n";
            $last_ofs = $end_ch + 2;
        }
    }
    $raw_out .= "\n" while ( length( $raw_out ) < $raw_ch_count );
    my $new_cksum = md5_hex( encode_utf8( $raw_out ));
    open( my $ofh, '>:utf8', $opath ) or die "ERROR: $opath open failed: $!\n";
    print $ofh $raw_out;
    close $ofh;
    if ( $new_cksum ne $raw_cksum ) {
        warn "ERROR: $opath cksum_mismatch: expecting $raw_cksum, got $new_cksum\n";
    }
}
