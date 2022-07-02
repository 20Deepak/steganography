import cv2  # open-cv library (pip install opencv-python)
import os

class MetaData:
    META_DATA_SIZE = 30

    
    @classmethod
    def compose_metadata(cls, filesize, filename):
        # 8 digits for the filesize (max 99 mb)
        if filesize > 99999999:
            raise Exception('Filesize Overflow')
        fs = str(filesize).rjust(8, '0')

        # 20 characters for filename
        # 2 characters as boundary <>
        fn = filename.rjust(20, '_')
        fn = fn[len(fn) - 20:]

        return '<' + fs + fn + '>'

    
    @classmethod
    def extract_data(cls, metadata):
        filesize = int(metadata[1:9])
        filename = metadata[9: len(metadata) - 1].strip('_')
        return filesize, filename


class Steganography:
    SPLIT_BITS = lambda n: (n >> 5, (n >> 2) & 7, n & 3)
    MERGE_BITS = lambda bits: (((bits[0] << 3) | bits[1]) << 2) | bits[2]

    def embed(self, image_path, data_file):
        # load the image in memory
        mem_image = cv2.imread(image_path)
        if mem_image is None:
            raise Exception(image_path + ' doesnt exist')
        print(mem_image.shape)

        # Compose the metadata
        data_file_size = os.stat(data_file).st_size
        header = MetaData.compose_metadata(data_file_size, os.path.basename(data_file))
        total_embedding = data_file_size + MetaData.META_DATA_SIZE

        # embedding capacity check
        if total_embedding > mem_image.shape[1] * mem_image.shape[0]:
            raise Exception('Embedding Capacity Overflow')

        # load the file in memory
        fh = open(data_file, 'rb')
        buffer = fh.read()
        fh.close()

        # Embedding
        index = 0
        r = 0
        while r < mem_image.shape[0] and index < total_embedding:
            c = 0
            while c < mem_image.shape[1] and index < total_embedding:
                # Embedding rule: First 30 bytes of header followed by the file content
                if index < MetaData.META_DATA_SIZE:
                    bits = Steganography.SPLIT_BITS(ord(header[index]))
                else:
                    bits = Steganography.SPLIT_BITS(buffer[index - MetaData.META_DATA_SIZE])

                # embed in pixel r,c
                for q in range(1, 4):  # 1,2,3
                    qty = 3 - q // 3
                    # Free the last qty bits of bands and embed the data bits
                    mem_image[r, c, q - 1] = mem_image[r, c, q - 1] >> qty
                    mem_image[r, c, q - 1] = mem_image[r, c, q - 1] << qty
                    mem_image[r, c, q - 1] = mem_image[r, c, q - 1] | bits[q - 1]

                index += 1
                c += 1
            r += 1

        # save back the target image
        cv2.imwrite('d:/temp/result.png', mem_image)
        print('See the result : d:/temp/result.png')

    def extract(self, has_embedding):
        # load the image in memory
        mem_vessel_image = cv2.imread(has_embedding)

        # know how much and what is embedded
        i = 0
        header = ''
        bits = []
        while i < MetaData.META_DATA_SIZE:
            r = i // mem_vessel_image.shape[1]
            c = i % mem_vessel_image.shape[1]
            bits.clear()
            for q in range(1, 4):  # 1,2,3
                qty = 3 - q // 3
                bits.append(mem_vessel_image[r, c, q - 1] & 2 ** qty - 1)

            header = header + chr(Steganography.MERGE_BITS(bits))
            i += 1

        # print(header)
        file_size, file_name = MetaData.extract_data(header)
        # print('Filesize: ', file_size)
        # print('Filename: ', file_name)

        #lets read filesize number of pixels from the image (offset by header size)
        i = MetaData.META_DATA_SIZE
        file_size += MetaData.META_DATA_SIZE

        #Open a file for writing the fetched bytes
        fn = 'd:/temp/' + file_name
        fh = open(fn, 'wb')

        while i < file_size:
            r = i // mem_vessel_image.shape[1]
            c = i % mem_vessel_image.shape[1]
            bits.clear()
            for q in range(1,4):
                qty = 3 - q //3
                bits.append(mem_vessel_image[r, c, q-1] & 2**qty-1)

            temp = int(Steganography.MERGE_BITS(bits))

            fh.write(int.to_bytes(temp, length=1, byteorder='big'))
            i+=1

        fh.close()

        print('See the result in : ', fn)

def main():
    while True:
        print('Welcome to Steganography System')
        print('1. Embedding ')
        print('2. Extraction ')
        print('3. Exit')
        print('Enter Choice')
        ch = int(input())
        if ch == 1:
            print('Enter the absolute path for the vessel file')
            vessel = input()
            print('Enter the absolute path for the file to be embedded')
            to_embed = input()
            sg = Steganography()
            sg.embed(vessel, to_embed)
        elif ch == 2:
            print('Enter the absolute path for the file having embedding')
            has_embedding = input()
            sg = Steganography()
            sg.extract(has_embedding)
        elif ch == 3:
            break
        else:
            print('Wrong Choice')

main()

