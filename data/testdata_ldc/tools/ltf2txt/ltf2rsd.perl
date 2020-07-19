#!/usr/bin/env perl

=head1 NAME

ltf2rsd.perl

=head1 LICENSE

ltf2rsd.perl is made available under the BSD 2-Clause License,
http://opensource.org/licenses/BSD-2-Clause.

Copyright (c) 2015 Trustees of the University of Pennsylvania

=head1 SYNOPSIS

  ltf2rsd.perl [-o output_dir] input_dir

=head1 DESCRIPTION

Given a (relative or absolute) directory path, this script will search
that path recursively for all data files that have a '.ltf.xml'
filename extension.  For each file found, it will recreate the
original "raw source data" (rsd.txt) file from which the ltf.xml was
derived.

By default, each output file will be placed in a directory called
"rsd" that sits adjacent to the "ltf" directory containing the
corresponding .ltf.xml file.

Use the "-o" option to select a different directory path for storing
the output source files.  In this case, the given "output_dir" will be
created if necessary, and any directory structure below the level of
the given "input_dir" will be replicated under "output_dir", with
"rsd" directories wherever the input path has an "ltf" directory.
Consider the following example:

# corpus X is stored on disk volume "/v1", and contains:

  /v1/X/data/
        type1/ltf -- contains 200 files: x*.ltf.xml
        type2/subtypeA/ltf -- contains 90 files: y*.ltf.xml
        type2/subtypeB/ltf -- contains 50 files: z*.ltf.xml

If ltf2rsd is run in default mode as follows:

  ltf2rsd /v1/X/data

the newly created output will be:

  /v1/X/data/
        type1/rsd -- contains 200 files: x*.rsd.txt
        type2/subtypeA/rsd -- contains 90 files: y*.rsd.txt
        type2/subtypeB/rsd -- contains 50 files: z*.rsd.txt

Alternately, you can specify another output path (where you have write
access), like this:

  ltf2rsd  -o /v2/workspace/X/data  /v1/X/data

In this case, the output path will be created if it doesn't already
exist (and if there are no permission problems), and subdirectories
and files will be created as needed; the end result will be:

  /v1/X/data/ -- all contents remain unchanged

  /v2/workspace/X/data/
        type1/rsd -- contains 200 files: x*.rsd.txt
        type2/subtypeA/rsd -- contains 90 files: y*.rsd.txt
        type2/subtypeB/rsd -- contains 50 files: z*.rsd.txt

There will always be a 1-line report on stderr, showing the path being
used for output.  Any problems that occur with the input or output
files will also be reported on stderr.

=head1 VERSION

This is ltf2rsd.perl version 1.1

=head1 AUTHOR

David Graff <graff@ldc.upenn.edu>

=cut

use strict;
use File::Spec;
use File::Path qw/make_path/;
use Digest::MD5 qw/md5_hex/;
use Encode qw/encode_utf8/;

my $Usage = "Usage: $0 [-o output_dir] input_dir\n";
my ( $inp_path, $out_path );
if ( @ARGV and -d $ARGV[-1] ) {
    $out_path = $inp_path = pop @ARGV;
}
if ( @ARGV == 2 and $ARGV[0] eq '-o' ) {
    shift @ARGV;
    $out_path = shift @ARGV;
    unless ( -d $out_path ) {
        make_path( $out_path );  # if this call fails, it "croaks", and we die right here.
    }
}

die $Usage unless ( $inp_path and @ARGV == 0 );

warn "$0: creating output files under $out_path\n";

my $out_spec = ( $inp_path eq $out_path ) ? '.'
    : ( File::Spec->file_name_is_absolute( $out_path )) ? $out_path
    : File::Spec->rel2abs( $out_path );

if ( $inp_path ne '.' ) {
    chdir( $inp_path ) or die "ERROR: chdir $inp_path: $!\n";
}
traverse( '.' );

sub traverse
{
    my ( $ipath ) = @_;
    opendir( my $dh, $ipath ) or die "ERROR: opendir $inp_path/$ipath: $!\n";
    my $opath = File::Spec->catdir( $out_spec, $ipath );
    $opath =~ s/\bltf\z/rsd/;
    unless ( -d $opath ) {
        make_path $opath or die "ERROR: mkdir $opath: $!\n";
    }
    while ( my $ifile = readdir( $dh )) {
        next if ( $ifile =~ /^\.\.?$/ );
        if ( -d "$ipath/$ifile" ) {
            traverse( "$ipath/$ifile" );
        }
        elsif ( $ifile =~ /\.ltf\.xml$/ ) {
            convert_and_save( "$ipath/$ifile", $opath );
        }
    }
}

sub convert_and_save
{
    my ( $ifile, $opath ) = @_;
    open( my $ifh, '<:utf8', $ifile ) or die "ERROR: open $ifile for input: $!\n";
    my $last_ofs = 0;
    my $raw_out = '';
    my ( $start_ch, $end_ch, $raw_ch_count, $raw_cksum );
    while ( <$ifh> ) {
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
    ( my $ofile = $ifile ) =~ s:.*/::;
    $ofile =~ s/ltf.xml\z/rsd.txt/;
    open( my $ofh, '>:utf8', "$opath/$ofile" ) or die "ERROR: $opath/$ofile open failed: $!\n";
    print $ofh $raw_out;
    close $ofh;
    if ( $new_cksum ne $raw_cksum ) {
        warn "ERROR: $opath/$ofile cksum_mismatch: expecting $raw_cksum, got $new_cksum\n";
    }
}
