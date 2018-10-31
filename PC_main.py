import sys
#call this script with arguments: "Cannabis 1" to merge; "Cannabis 2" to merge and clean; and "Cannabis 3" to merge, clean, and perform other final steps
#replace "Cannabis" with "Opioid" in the arguments depending on which project is being worked on


def main():

    if sys.argv[1] != "Cannabis" and sys.argv[1] != "Opioid":
        print("{} is not a valid drug type. Please enter 'Cannabis' or 'Opioid'".format(sys.argv[1]))
        sys.exit()
    else:
        main_drug = sys.argv[1] # Cannabis or Opioid
    
    x = int(sys.argv[2])
    
    if x >= 1 and x <= 3:
        if x >= 1:
            import PC_Merge
            PC_Merge.main()
        if x >= 2:
            import PC_Clean
            PC_Clean.main()
        if x == 3:
            import PC_separate_categories
            PC_separate_categories.main(main_drug)
    else:
        print("{} is not a valid argument. Please enter '1', '2', or '3'".format(sys.argv[2]))

if __name__ == "__main__":
    main()