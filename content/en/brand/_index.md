---
title: Brand
description: The Blowhorn logo, wordmark, colors, type, Major Blowhorn and Old Thunderlung, with the rules for using them and two kits to download.
lead: The logo, the colors, the type and one opinionated rooster. Everything you need to show Blowhorn off without upsetting him.
layout: brand
lastmod: 2026-11-01
sitemap:
  changefreq: monthly
  priority: 0.3
# Both zips are built from the brand masters by the product repository's
# tools/scripts/brand/build-brand-kit.py and copied to static/brand/ unchanged.
# `size` is the file's size in MB (1024 x 1024 bytes): one decimal under 10 MB,
# whole MB above. make check-brand-kits fails when it drifts from the file.
kits:
  full:
    url: /brand/blowhorn-brand-kit.zip
    size: 35 MB
  logos:
    url: /brand/blowhorn-logo-kit.zip
    size: 2.0 MB
# Logo tiles. `stage` is the ground the file is drawn for: light, dark, teal or charcoal.
lockups:
  - name: Horizontal lockup
    note: The default
    file: blowhorn-lockup-horizontal.svg
    stage: light
    w: 584
    h: 145
  - name: Horizontal lockup, on dark
    note: For near black and charcoal
    file: blowhorn-lockup-horizontal-on-dark.svg
    stage: dark
    w: 584
    h: 145
  - name: Stacked lockup
    note: For square spaces
    file: blowhorn-lockup-stacked.svg
    stage: light
    w: 430
    h: 318
  - name: Stacked lockup, on dark
    note: For square spaces on dark
    file: blowhorn-lockup-stacked-on-dark.svg
    stage: dark
    w: 430
    h: 318
marks:
  - name: Icon
    note: When the name is already nearby
    file: blowhorn-icon.svg
    stage: light
  - name: Icon, on dark
    note: The mouthpiece turns teal
    file: blowhorn-icon-on-dark.svg
    stage: dark
  - name: One color, charcoal
    note: On teal, photos and busy grounds
    file: blowhorn-icon-mono-charcoal.svg
    stage: teal
  - name: One color, white
    note: On dark photos and busy grounds
    file: blowhorn-icon-mono-white.svg
    stage: charcoal
wordmarks:
  - name: Wordmark
    note: Outlined art, never a font
    file: blowhorn-wordmark.svg
    stage: light
  - name: Wordmark, on dark
    note: White, for dark grounds
    file: blowhorn-wordmark-white.svg
    stage: dark
  - name: Company lockup
    note: The formal lockup, with the company mark
    file: layer5-blowhorn-lockup.svg
    stage: light
  - name: Company lockup, on dark
    note: The same, after hours
    file: layer5-blowhorn-lockup-on-dark.svg
    stage: dark
  - name: One-color lockup, charcoal
    note: For teal and busy light grounds
    file: blowhorn-lockup-horizontal-mono-charcoal.svg
    stage: teal
  - name: One-color lockup, white
    note: For busy dark grounds
    file: blowhorn-lockup-horizontal-mono-white.svg
    stage: charcoal
apps:
  - name: App icon
    file: blowhorn-app-icon.svg
  - name: App icon, dark
    file: blowhorn-app-icon-dark.svg
  - name: App icon, light
    file: blowhorn-app-icon-light.svg
mascot:
  - name: Hat, facing left
    file: locked-6/major-6-hat-left
    alt: Major Blowhorn in his campaign hat, pointing and shouting into his bullhorn, facing left
    w: 657
    h: 560
  - name: Hat, facing right
    file: locked-6/major-6-hat-right
    alt: Major Blowhorn in his campaign hat, pointing and shouting into his bullhorn, facing right
    w: 657
    h: 560
  - name: Medals
    file: locked-6/major-6-medals-right
    alt: Major Blowhorn with his medals, shouting into his bullhorn
    w: 660
    h: 560
  - name: Plain
    file: locked-6/major-6-plain-left
    alt: Major Blowhorn without his hat, shouting into his bullhorn
    w: 659
    h: 560
# Old Thunderlung tiles: PNG and WebP copies of the product repository's
# marketing/cast/major-blowhorn/thunderlung/brand-style/ cutouts, unchanged.
thunderlung:
  - name: With cord, side
    file: thunderlung/thunderlung-tassel-side
    alt: Old Thunderlung, a dented brass army bugle with a red cord and two tassels, seen from the side
    w: 1173
    h: 660
  - name: With cord, three-quarter
    file: thunderlung/thunderlung-tassel-3q
    alt: Old Thunderlung, a dented brass army bugle with a red cord and two tassels, at a three-quarter angle
    w: 1110
    h: 641
  - name: Plain, side
    file: thunderlung/thunderlung-notassel-side
    alt: Old Thunderlung, a dented brass army bugle without its cord, seen from the side
    w: 1172
    h: 611
  - name: Plain, tilted
    file: thunderlung/thunderlung-notassel-tilt
    alt: Old Thunderlung, a dented brass army bugle without its cord, tilted bell up
    w: 963
    h: 725
# Cast tiles: WebP masters in static/assets/brand/troops/ (<file>.webp) with a 640 px
# display copy (<file>-640.webp). w and h are the display copy size.
troops:
  - name: "Chief Drill Instructor"
    file: drill-instructor
    alt: "Chief Drill Instructor, one of the Blowhorn troops"
    w: 640
    h: 360
  - name: "Corporal Clover"
    note: "The run log and ledgers"
    file: corporal-clover
    alt: "Corporal Clover, one of the Blowhorn troops, in charge of the run log and ledgers"
    w: 640
    h: 640
  - name: "The General"
    note: "Strategy and results"
    file: general
    alt: "The General, one of the Blowhorn troops, in charge of strategy and results"
    w: 640
    h: 360
  - name: "GI Donkey"
    file: gi-donkey
    alt: "GI Donkey, one of the Blowhorn troops"
    w: 640
    h: 360
  - name: "Keyboard Warrior"
    note: "The command line"
    file: keyboard-warrior
    alt: "Keyboard Warrior, one of the Blowhorn troops, in charge of the command line"
    w: 640
    h: 360
  - name: "Mouse Marine"
    note: "Profiles and the desktop app"
    file: mouse-marine
    alt: "Mouse Marine, one of the Blowhorn troops, in charge of profiles and the desktop app"
    w: 640
    h: 360
  - name: "Platoon Private"
    file: platoon-private
    alt: "Platoon Private, one of the Blowhorn troops"
    w: 640
    h: 360
  - name: "Recruit Chick"
    file: recruit-chick
    alt: "Recruit Chick, one of the Blowhorn troops"
    w: 640
    h: 360
  - name: "Robo-Recruit"
    note: "Routines and previews"
    file: robo-recruit
    alt: "Robo-Recruit, one of the Blowhorn troops, in charge of routines and previews"
    w: 640
    h: 360
  - name: "Sergeant Steady"
    note: "Steady delivery, mail and schedules"
    file: sergeant-steady
    alt: "Sergeant Steady, one of the Blowhorn troops, in charge of steady delivery, mail and schedules"
    w: 640
    h: 360
  - name: "Sleeper Cell"
    note: "The schedule and the computer on watch"
    file: sleeper-cell
    alt: "Sleeper Cell, one of the Blowhorn troops, in charge of the schedule and the computer on watch"
    w: 640
    h: 360
  - name: "Staff Sergeant Red Flag"
    note: "Go and no-go calls"
    file: staff-sergeant-red-flag
    alt: "Staff Sergeant Red Flag, one of the Blowhorn troops, in charge of go and no-go calls"
    w: 640
    h: 640
  - name: "Trench Trooper"
    note: "The browser extension"
    file: trench-trooper
    alt: "Trench Trooper, one of the Blowhorn troops, in charge of the browser extension"
    w: 640
    h: 360
recruits:
  - name: "Bantam Rooster"
    file: rooster
    alt: "A tiny bantam rooster, no bigger than a chick, white feathers speckled with near-black, a small coral-shade comb and wattle, yellow-shade beak and legs."
    w: 640
    h: 360
  - name: "Bugler Chick"
    file: bugler-chick
    alt: "A small Recruit Chick bugler who sounds the call for the squad."
    w: 640
    h: 360
  - name: "The Buzz Brigade"
    file: honeybee
    alt: "The Buzz Brigade, five round, fuzzy honeybees flying in a loose cluster with clear gaps between them, yellow and leather stripes, light gray wings."
    w: 640
    h: 360
  - name: "Captain Gallop"
    note: "Cavalry of Many Profiles"
    file: horse
    alt: "Captain Gallop, a proud horse rearing up on his hind legs, chestnut coat in khaki-shade, mane and tail in leather."
    w: 640
    h: 360
  - name: "Colonel Plume"
    note: "Launch Day"
    file: peacock
    alt: "Colonel Plume, a proud peacock standing tall, his body, neck and crest all white (a real peafowl breed)."
    w: 640
    h: 360
  - name: "Corporal Hum"
    note: "Pause and Resume"
    file: alpaca
    alt: "Corporal Hum, a round, very fluffy alpaca standing on her hind legs, fawn khaki fleece with a big pom-pom topknot."
    w: 640
    h: 360
  - name: "Corporal Twinstop"
    note: "Duplicate Guard"
    file: llama
    alt: "Corporal Twinstop, a cream llama in a striped blanket, drops a boom gate on a duplicate envelope and spits at it."
    w: 640
    h: 360
  - name: "Inspector Whiskers"
    note: "Fake Patrol"
    file: barn-cat
    alt: "Inspector Whiskers, a sleek tabby barn cat standing on her hind legs, amber fur with khaki-shade stripes, white muzzle and chest."
    w: 640
    h: 360
  - name: "Lance Corporal Squeak"
    note: "Slack Recon"
    file: mouse
    alt: "Lance Corporal Squeak, a tiny field mouse tiptoeing on two legs, gray fur, cream belly and inner ears, big round ears, long curling tail."
    w: 640
    h: 360
  - name: "Mama Pekin and the Ducks-in-a-Row Brigade"
    file: duck-pekin
    alt: "Mama Pekin, a Pekin duck waddling on two webbed feet, white feathers, amber bill and feet, followed by four small ducklings."
    w: 640
    h: 360
  - name: "The Mud Crew"
    note: "Trench Trooper's pigs"
    file: pig
    alt: "Three muddy pigs of the Mud Crew, in charcoal helmets, trot along hauling tall stacks of paper."
    w: 640
    h: 360
  - name: "Night Watch Officer Hoot"
    file: barn-owl
    alt: "Night Watch Officer Hoot, a barn owl perched on a flat khaki-shade wooden beam, white heart-shaped face, khaki wings and back, cream chest."
    w: 640
    h: 360
  - name: "Pigeon Couriers"
    file: pigeon-couriers
    alt: "Pigeon couriers who carry messages for the squad."
    w: 640
    h: 360
  - name: "Pony Express Private Penny"
    note: "LinkedIn Outreach"
    file: pony
    alt: "Pony Express Private Penny, a small dappled pony trotting on all four legs, silver gray coat with gray dapples, slate mane and tail."
    w: 640
    h: 360
  - name: "Private Fleece"
    note: "Practice Range"
    file: lamb
    alt: "Private Fleece, a small fluffy lamb standing on her hind legs, white wool, cream face, ears and legs."
    w: 640
    h: 360
  - name: "Private Hopkins"
    note: "Command Line Corps"
    file: rabbit
    alt: "Private Hopkins, a lively rabbit, brown khaki-shade fur, cream belly, one ear up and one ear flopped."
    w: 640
    h: 360
  - name: "Private Pot-Rack"
    note: "Lookout"
    file: guinea-fowl
    alt: "Private Pot-Rack, a round guinea fowl, slate feathers covered in small white polka dots, a bare white face, small coral-shade wattles, a yellow-shade beak."
    w: 640
    h: 360
  - name: "Ranger Kid"
    note: "Hacker News Climber"
    file: goat-young
    alt: "Ranger Kid, a small nimble young goat, clearly a child, brown khaki-shade coat, tiny cream nub horns, no beard."
    w: 640
    h: 360
  - name: "Scout Biscuit"
    note: "Discovery Hound"
    file: farm-dog
    alt: "Scout Biscuit, a floppy-eared farm hound trotting on all four legs, white coat with big khaki-shade patches and leather ears."
    w: 640
    h: 360
  - name: "Sergeant Collie"
    note: "Profile Herder"
    file: sheepdog
    alt: "Sergeant Collie, an alert border collie crouched low on all four legs in a herding stance, near-black and white coat."
    w: 640
    h: 360
  - name: "Sergeant Mother Hen"
    file: chicken-hen
    alt: "Sergeant Mother Hen, a plump mother hen (clearly a hen: small low comb, short rounded tail, no long tail plumes), brown khaki-shade feathers with cream speckles, a small coral-shade comb and wattle, a yellow-shade beak."
    w: 640
    h: 360
  - name: "Supply Mule Sarge"
    file: mule
    alt: "Supply Mule Sarge, a sturdy mule standing on all four legs, dark brown leather coat, cream muzzle, very long ears."
    w: 640
    h: 360
  - name: "Turkey Cadets"
    note: "The Chief Drill Instructor's cadets"
    file: turkey
    alt: "Three skinny, gangly young turkey cadets, smaller than the Chief Drill Instructor, khaki-shade and leather feathers, bare silver gray heads with small coral-shade wattles."
    w: 640
    h: 360
  - name: "Wing Commander Vee"
    note: "Team Amplification"
    file: goose
    alt: "Wing Commander Vee, a Canada goose in flight, gray body and wings, near-black neck and head, a white chin-strap patch."
    w: 640
    h: 360
troublemakers:
  - name: "Algorithm Fog"
    file: algorithm-fog
    alt: "A rolling wall of faceted charcoal fog, the villain that hides posts from the feed."
    w: 640
    h: 360
  - name: "Bot Swarm"
    file: bot-swarm
    alt: "A swarm of tiny identical charcoal bots doing the same thing over and over."
    w: 640
    h: 360
  - name: "Clone Army"
    file: clone-army
    alt: "Floating identical masks over hollow bodies, the fake-account clone army."
    w: 640
    h: 360
  - name: "The Noise"
    file: the-noise
    alt: "The Noise: a chaotic cloud of shouting clutter that drowns out real posts."
    w: 640
    h: 360
  - name: "Password Houseguest"
    file: password-houseguest
    alt: "A smiling houseguest who keeps asking for your passwords and keys."
    w: 640
    h: 640
  - name: "Scarecrows"
    file: scarecrows
    alt: "Bought-follower scarecrows: hollow scarecrows holding up thumbs-up shapes."
    w: 640
    h: 360
  - name: "Spam Gremlins"
    file: spam-gremlins
    alt: "Small spam gremlins wearing envelope hats."
    w: 640
    h: 360
fonts:
  - family: Bricolage Grotesque
    role: Display
    class: type-display
    weights: ExtraBold 800, Bold 700
    sample: One message out, many ears in
    url: https://fonts.google.com/specimen/Bricolage+Grotesque
  - family: Instrument Sans
    role: Text and interface
    class: type-sans
    weights: Regular 400, Medium 500, SemiBold 600
    sample: Write it once. Blowhorn takes it from there.
    url: https://fonts.google.com/specimen/Instrument+Sans
  - family: JetBrains Mono
    role: Code and labels
    class: type-mono
    weights: Regular 400, Medium 500
    sample: POSTED TO 12 PROFILES
    url: https://fonts.google.com/specimen/JetBrains+Mono
---
