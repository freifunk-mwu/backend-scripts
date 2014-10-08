#!/usr/bin/perl
use strict;
use warnings;

# no flags or arguments permitted
die "unexpected arguments, stopped" unless( @ARGV == 0 );

# will be a hash of array references; array hold respective peers
my(@nodelist) = ();
my(%nodes) = ();
my(%edges) = ();

# read dot file into hash; reduce directed graph to undirected
#digraph {
#        augsburg1 [label = "augsburg1"];

while( <STDIN> ) {
  if( /\w+ \[label = "(\w+)"\];/ ) {
    push @nodelist, $1;
#    print STDERR ( "erkannt: node $1\n" );
  }
  if( /(\w+) -> (\w+);/ ) {
    my $reverse_set_ref = $edges{$2};
#    print STDERR ((defined $reverse_set_ref) ? "... $reverse_set_ref @$reverse_set_ref\n" : "...  -undef-\n");
    if( ( ! defined $reverse_set_ref ) ||
        ( (grep {$_ eq $1} @$reverse_set_ref) == 0 ) ) {
      # reverse link is not stored yet, so add (or replace) forward one
      my($forward_set_ref) = $edges{$1};
      if( defined $forward_set_ref ) {
        if( (grep {$_ eq $2} @$forward_set_ref) == 0 ) {
          push @$forward_set_ref, $2;
        } else {
          warn "$1 -> $2 already in";
        }
      } else {
        $edges{$1} = [$2];
      }
#      print STDERR ( "+" );
    }# else {
#      print STDERR ( "-" );
#    }
#    print STDERR ( " $1 nach $2\n" );
  }
}

# write out undirected graph as json
#{
#  "nodes":[
#    {"name":"Myriel","group":1},

print( "{\n  \"nodes\":[\n" );
# nodes
my($i) = 0;
foreach(@nodelist) {
  my($group) = 1;
  $group = 2 if( (/wiesbaden/) || (/mainz/) );
  print( ",\n" ) if( $i > 0 );  # end previous line if there was a previous line
  print( "    {\"name\":\"$_\",\"group\":$group}" );   # don't end line here
  $nodes{$_} = $i++;
}
print( "\n  ],\n  \"links\":[\n" );
#edges
my($j) = 0;
foreach(keys %edges) {
  my($llocal) = 0;
  $llocal = 1 if( (/wiesbaden/) || (/mainz/) );
  my($left_inx) = $nodes{$_};
  my($peers_ref) = $edges{$_};
  foreach(@$peers_ref) {
    my($rlocal) = 0;
    $rlocal = 1 if( (/wiesbaden/) || (/mainz/) );
    my($right_inx) = $nodes{$_};
    my($value) = 2;
    if( $llocal && $rlocal ) {
      $value = 3;
    } elsif( $llocal || $rlocal ) {
      $value = 1;
    }
    print( ",\n" ) if( $j > 0 );  # end previous line if there was a previous line
    print( "    {\"source\":$left_inx,\"target\":$right_inx,\"value\":$value}" );  # don't end line here
    $j++;
  }
}
print( "\n  ]\n}\n" );
