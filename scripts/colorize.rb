#!/usr/bin/env ruby
# encoding: utf-8
#
# How does it work:
#   puts "\e[31m" + "hello" + "\e[0m" + "world"
# 1. \e[31m make color red
# 2. \e[0m reset color
# 3. so it prints a red "hello" and a normal "world"

# require 'ap'
# require 'awesome_print'

def debugging?; false; end

module Colorize
  def start_color(color_code)
    "\e[#{color_code}m"
  end

  def end_color
    "\e[0m"
  end

  # set string color
  def self.colorize(str, color_code)
    pre = start_color(color_code)
    post = end_color
    pre + str + post
  end

  # get all foreground color codes
  def self.all_fg_code
    MY_COLOR_CODE.select {|key, _|
      next false if key == :fg_black
      next false if key == :fg_darkgray

      key.to_s.match /^fg_/
    }
  end

  # get all background color codes
  def self.all_bg_code
    MY_COLOR_CODE.select {|key, _|
      key.to_s.match /^bg_/
    }
  end

  # generate a color code by given index, or a random color code if index is not given
  def gen_color_code code = nil, all_codes = nil
    all_codes = self.all_fg_code.merge(self.all_bg_code) if all_codes.nil?
    if code
      index = code.to_i % all_codes.values.length
      return all_codes.values[index]
    else
      fgcolors = ['fg_lightred', 'fg_green', 'fg_blue','fg_magenta', 'fg_cyan', 'fg_darkgray', 'fg_lightgreen', 'fg_lightyellow', 'fg_lightblue', 'fg_lightmagenta']
      index = Random.rand fgcolors.length
      return MY_COLOR_CODE[fgcolors[index].to_sym]
    end
  end

  def remove_color
      gsub(/\x1B\[([0-9]{1,3}(;[0-9]{1,3}(;[0-9]{1,3}(;[0-9]{1,3})?)?)?)?[m|K]/, '')
  end

  class << self
      # e.g. #green => #fg_green
      def method_missing name, *args
        method = MY_COLOR_CODE[name.to_sym] || MY_COLOR_CODE["fg_#{name}".to_sym]
        start_color method if method
      end
  end

  # export these functions so we can just Colorize::xxx
  module_function :start_color, :end_color, :gen_color_code #, :colorize

  # method name => color code:
  # ref: http://misc.flogisoft.com/bash/tip_colors_and_formatting
  MY_COLOR_CODE = color_code = {
      :no_color     => 0, # reset all attributes
      :bright       => 1,
      :dim          => 2,
      :underline    => 4,
      :blink        => 5,
      :swapcolor    => 7, # invert
      :bg_color     => 8, # hidden(e.g. for password)
      :strikethrough => 9,
      :fg_black     => 30,
      :fg_red       => 31,
      :fg_green     => 32,
      :fg_yellow    => 33,
      :fg_blue      => 34,
      :fg_magenta   => 35,
      :fg_cyan      => 36,
      :fg_lightgray => 37, # light gray
      :fg_default   => 39,

      :fg_darkgray  => 90, # dark gray
      :fg_lightred  => 91,
      :fg_lightgreen => 92,
      :fg_lightyellow => 93,
      :fg_lightblue => 94,
      :fg_lightmagenta => 95,
      :fg_lightcyan => 96,
      :fg_white     => 97,

      :bg_black     => 40,
      :bg_red       => 41,
      :bg_green     => 42,
      :bg_yellow    => 43,
      :bg_blue      => 44,
      :bg_magenta   => 45,
      :bg_cyan      => 46,
      :bg_lightgray => 47, # light gray
      :bg_default   => 49,

      :bg_darkgray  => 100,
      :bg_lightred  => 101,
      :bg_lightgreen => 102,
      :bg_lightyellow => 103,
      :bg_lightblue => 104,
      :bg_lightmagenta => 105,
      :bg_lightcyan => 106,
      :bg_white     => 107,
  }

  Colorize::MY_COLOR_CODE.each_pair do |name ,code|
    # define all fg_xxx & bg_xxx methods
    define_method name do
      pre = Colorize.start_color(code)
      pre
    end

    # Alias xxx to fg_xxx
    if name.match /fg_(.*)/
      alias_method $1, name
    end
  end
end

class String
  include Colorize
    # all colors are stored in @colors_at, but only apply/combine them when needed
    def add_color from, to, color
        return if color.to_s.empty?
        colors = color.split(/[,:]/)

        # puts "#{color}: #{from}->#{to}" if debugging?

        @colors_at = {} unless @colors_at

        @colors_at[from] = [] unless @colors_at[from]
        @colors_at[to] = [] unless @colors_at[to]

        @colors_at[from] += colors         # in stack
        @colors_at[to].unshift :no_color    #
    end

    attr_reader :colors_at

    # matches() is like match(), except matches() returns all matches as an
    #   array of MatchData, while match() returns only the first match.
    #   ref: http://stackoverflow.com/questions/9528035/ruby-stringscan-equivalent-to-return-matchdata
    def matches(pattern)
        start_pos = 0
        rv = []
        while(m = match(pattern, start_pos))
            rv.push(m)
            break if m.end(0) == start_pos
            start_pos = m.end(0)
        end
        rv
    end

    # set string color
    def colorize(color_code)
      Colorize.colorize(self, color_code)
    end

    def colorize_random(code = nil)
        colorize(Colorize::gen_color_code(code))
    end

    def remove_color
        Colorize.instance_method(:remove_color).bind(self).call
    end

    Colorize::MY_COLOR_CODE.each_pair do |name, code|
        define_method name do
            colorize(code) # wrap string with given color
        end

        # Alias xxx to fg_xxx
        if name.match /fg_(.*)/
            alias_method $1, name
        end
    end

    def highlight(pattern, colors)
        colors = [colors] unless colors.is_a? Array

        matches_list = matches(pattern)
        return self if matches_list.empty?

        new_self = self.clone

        rv = ''
        grp_len = matches_list[0].length - 1
        # change backwards, so start_pos and end_pos won't change
        matches_list.reverse.each do |matches|
            if matches.length == 1 # only one group, highlight group[0]
                toGrp = 0
            else
                toGrp = 1         # highlight all groups except group[0]
            end

            matches_sorted = (matches.length - 1).downto(toGrp).map {|grp|
                {
                    :start_pos => matches.begin(grp),
                    :end_pos => matches.end(grp),
                    :data => matches[grp],
                    :grp => grp,
                }
            }.select{|it| it[:data] }.sort_by {|it|
                [it[:end_pos], it[:grp]]
            }.reverse

            # loop each match group:
            matches_sorted.each do |match|
                grp = match[:grp]
                add_color match[:start_pos], match[:end_pos], colors[grp-1]
            end
        end

        return new_self unless colors_at

        ap colors_at if debugging?
        colors_at.keys.sort.reverse.each do |pos|
            new_self.insert pos, colors_at[pos].map{|c| Colorize.send(c.to_sym)}.join
        end

        new_self
    end

    def highlight_at(positions, color = 'fg_yellow')
        return self if positions.empty?

        new_self = self.clone

        # change backwards, so start_pos and end_pos won't change
        positions.sort.reverse.each do |position|
            new_self[position..position] = "#{new_self[position]}".fg_yellow.swapcolor if new_self.length > position
        end

        new_self
    end

    def colorize_by_pattern pattern, method
    end
end

if __FILE__ == $PROGRAM_NAME
    VERBOSE = ARGV.delete('--verbose') or ARGV.delete('-v')
    if ARGV.delete('--help') or ARGV.delete('-h') or (ARGV.length == 0 and STDIN.tty?)
        puts "USAGE: #{File.basename __FILE__} REGEXP_PATTERN GROUP1_FG:GROUP1_BG [GROUP2_FG:GROUP2_BG ...]"
        # puts "E.g:   echo hello, owrld | #{File.basename __FILE__} '[lo]' bg_red | #{File.basename __FILE__} 'wr' fg_blue"
        puts "E.g:"
        puts "  echo hello, owrld | #{File.basename __FILE__}  '(ll).*(ld)' red:bg_blue blue:bg_red"
        puts "  echo hello, owrld | #{File.basename __FILE__}  '(l).*(ld)' red bg_red"
        puts "  echo hello, owrld | #{File.basename __FILE__}  'l.*,' yellow"
        exit 0
    end

    pattern = ARGV.shift || '(.*)'
    pattern = Regexp.new(pattern, Regexp::IGNORECASE)
    colors = ARGV.length >0 ? ARGV : ['black:bg_yellow:swapcolor']

    STDIN.each do |line|
        # puts line.gsub(pattern, '\0'.send(colors[0].to_sym))
        puts line.highlight(pattern, colors)
        puts line.colors_at if debugging?
        # puts line.highlight(pattern, colors1)
        STDOUT.flush
    end
end
