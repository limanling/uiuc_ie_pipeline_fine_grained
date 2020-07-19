#!/usr/bin/env perl

=head1 NAME

ltf2ma.perl

=head1 LICENSE

ltf2ma.perl is made available under the BSD 2-Clause License,
http://opensource.org/licenses/BSD-2-Clause.

=head1 SYNOPSIS

   ltf2ma.perl  [-o output_dir]  path/to/morph_alignment

=head1 DESCRIPTION

Given a (relative or absolute) directory path, this script will search
that path recursively for all data files that have a '.ltf.xml'
filename extension.  For each of these, it will create a corresponding
"morpheme-segment tokenized text" file ('.ma_tkn.txt') that can be
used in combination with the morphological alignment annotation files
(*.ma_ann.txt files in data/annotation/morph_alignment/ma_ann/), where
alignments between English and the target language are expressed in
terms of morpheme-segment token offsets (not character offsets) within
a matched pair of "*.ma_tkn.txt" files.

This script is tailored for use within the context of a DARPA LORELEI
language pack.  The directory path given as input is expected to
contain subdirectories for English and the target language, and each
of this is expected to contain an "ltf" directory.

By default, the output files will be created in "ma_tkn" directories
that exist (or are created if necessary) next to the input "ltf"
directories.

Use the "-o output_dir" option on the command line to use (or create)
output directories somewhere else.  In this case, the two language
directories and their ltf subdirectories will be created if necessary.

=head1 VERSION

This is ltf2ma.perl version 1.0

=head1 AUTHOR

David Graff <graff@ldc.upenn.edu>

=cut

use strict;
use File::Spec;
use File::Path qw/make_path/;
use Encode qw/encode_utf8/;

my $Usage = "Usage: $0 [-o output_dir] path/to/morph_alignment\n";
my ( $inp_path, $out_path );
if ( @ARGV and -d $ARGV[-1] ) {
    $out_path = $inp_path = pop @ARGV;
}
if ( @ARGV == 2 and $ARGV[0] eq '-o' ) {
    shift @ARGV;
    $out_path = shift @ARGV;
    unless ( -d $out_path ) {
        make_path( $out_path ); # if this call fails, it "croaks", and we die right here.
    }
}
warn "$0: creating output files under $out_path\n";

die $Usage unless ( $inp_path and @ARGV == 0 );

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
    $opath =~ s/\bltf\z/ma_tkn/;
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
        if ( /<TOKEN .*? morph="(.*?)" start_char.*?>(.*?)</ ) {
            my ( $morph, $token ) = ( $1, $2 );
            if ( $morph eq 'none' ) {
                $raw_out .= "$token ";
            }
            else {
                my $div = ( $morph =~ /:/ ) ? ':' : '=';
                my @morphs = map { s/$div.*//; $_ } split( /\s+/, $morph );
                $raw_out .= join( " ", @morphs ). " ";
            }
        }
        elsif ( /<\/SEG>/ ) {
            $raw_out =~ s/ *$/\n/;
        }
    }
    ( my $ofile = $ifile ) =~ s:.*/::;
    $ofile =~ s/ltf.xml\z/ma_tkn.txt/;
    open( my $ofh, '>:utf8', "$opath/$ofile" ) or die "ERROR: $opath/$ofile open failed: $!\n";
    print $ofh $raw_out;
    close $ofh;
}
